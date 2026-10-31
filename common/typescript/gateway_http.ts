/** OAuth resource server for the native multi-upstream gateway. No bearer forwarding. */
import { AsyncLocalStorage } from 'node:async_hooks';
import { createPublicKey, verify } from 'node:crypto';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { createMcpHandler } from '@modelcontextprotocol/server';
import { z } from 'zod';
import { nativeWorkspace } from './workspace.ts';
import { type Identity } from './gateway.ts';
import { RateLimit, publicEndpoint } from './advanced_policy.ts';

const headerSchema = z.object({ alg: z.literal('RS256'), kid: z.string().min(1).max(200), crit: z.never().optional() });
const claimsSchema = z.object({ iss: z.string(), aud: z.union([z.string(), z.array(z.string())]), sub: z.string().min(1).max(200), exp: z.number().finite(), iat: z.number().finite(), nbf: z.number().finite().optional(), scope: z.string().max(2000).default('') });
export class JwksVerifier {
  private keys: { kty: string; kid: string; n: string; e: string }[] = [];
  private expires = 0;
  private lastRefresh = -Infinity;
  private refreshing?: Promise<void>;
  constructor(readonly issuer: string, readonly resource: string, readonly jwksUrl: string, readonly fetcher: typeof fetch = fetch) {
    publicEndpoint(issuer); publicEndpoint(resource);
    // The operator pins this back-channel URL. It never comes from a JWT or discovery.
    const url = new URL(jwksUrl);
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.hash) throw new Error('Invalid pinned JWKS URL');
  }
  private async refresh() {
    if (this.refreshing) return this.refreshing;
    if (Date.now() - this.lastRefresh < 5000) throw new Error('JWKS refresh cooling down');
    this.lastRefresh = Date.now();
    this.refreshing = (async () => {
      const response = await this.fetcher(this.jwksUrl, { redirect: 'error', signal: AbortSignal.timeout(5000) });
      if (!response.ok || !response.body) throw new Error('JWKS unavailable');
      const reader = response.body.getReader(); let size = 0; const chunks: Uint8Array[] = [];
      try { while (true) { const part = await reader.read(); if (part.done) break; size += part.value.length; if (size > 64000) throw new Error('JWKS too large'); chunks.push(part.value); } }
      finally { await reader.cancel(); }
      const value = z.object({ keys: z.array(z.record(z.string(), z.unknown())).min(1).max(20) }).parse(JSON.parse(Buffer.concat(chunks).toString()));
      const signing = z.object({ kty: z.literal('RSA'), kid: z.string().min(1).max(200), n: z.string(), e: z.string(), alg: z.literal('RS256').optional(), use: z.literal('sig').optional(), key_ops: z.array(z.literal('verify')).optional() });
      // Issuers may also publish encryption or other-algorithm keys. They are
      // never candidates for an RS256 access-token signature.
      const keys = value.keys.flatMap(key => { const parsed = signing.safeParse(key); return parsed.success ? [parsed.data] : []; });
      if (!keys.length || new Set(keys.map(k => k.kid)).size !== keys.length) throw new Error('Missing or ambiguous signing keys');
      this.keys = keys; this.expires = Date.now() + 60000;
    })().finally(() => { this.refreshing = undefined; });
    return this.refreshing;
  }
  async verify(token: string): Promise<Identity> {
    if (token.length > 16000 || !/^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/.test(token)) throw new Error('Invalid token');
    const [head, body, signature] = token.split('.');
    const header = headerSchema.parse(JSON.parse(Buffer.from(head, 'base64url').toString()));
    if (this.expires <= Date.now() || !this.keys.some(k => k.kid === header.kid)) await this.refresh();
    const key = this.keys.find(k => k.kid === header.kid);
    if (!key || !verify('RSA-SHA256', Buffer.from(`${head}.${body}`), createPublicKey({ key, format: 'jwk' }), Buffer.from(signature, 'base64url'))) throw new Error('Invalid signature');
    const claims = claimsSchema.parse(JSON.parse(Buffer.from(body, 'base64url').toString()));
    const now = Date.now() / 1000;
    if (claims.iss !== this.issuer || ![claims.aud].flat().includes(this.resource) || claims.exp <= now || claims.iat > now + 30 || (claims.nbf ?? 0) > now || claims.exp <= claims.iat) throw new Error('Invalid claims');
    return { subject: claims.sub, scopes: claims.scope.split(' ').filter(Boolean) };
  }
}

export type GatewayOptions = { issuer: string; resource: string; jwksUrl: string; port?: number; bind?: string; upstreamMode?: 'memory' | 'stdio'; verifier?: Pick<JwksVerifier, 'verify'> };
export async function oauthGateway(options: GatewayOptions) {
  const resource = new URL(publicEndpoint(options.resource));
  const verifier = options.verifier ?? new JwksVerifier(options.issuer, options.resource, options.jwksUrl);
  const context = new AsyncLocalStorage<Identity>();
  const workspace = await nativeWorkspace(() => { const identity = context.getStore(); if (!identity) throw new Error('Identity required'); return identity; }, options.upstreamMode);
  const handler = createMcpHandler(workspace.factory, { legacy: 'reject', maxRequestBodySize: 64000 });
  const limit = new RateLimit(180);
  const metadataPath = '/.well-known/oauth-protected-resource' + resource.pathname;
  const metadataUrl = resource.origin + metadataPath;
  const server = createServer(async (req, res) => {
    res.setHeader('Cache-Control', 'no-store'); res.setHeader('X-Content-Type-Options', 'nosniff');
    try {
      const address = server.address(); const port = typeof address === 'object' && address ? address.port : options.port;
      if (req.url === '/readyz' && req.headers.host === `127.0.0.1:${port}` && !req.headers.origin) { res.end('ready'); return; }
      if (req.headers.host !== resource.host) { res.writeHead(421).end(); return; }
      if (req.headers.origin && req.headers.origin !== resource.origin) { res.writeHead(403).end(); return; }
      if (req.method === 'GET' && [metadataPath, '/.well-known/oauth-protected-resource'].includes(req.url ?? '')) {
        res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify({ resource: options.resource, authorization_servers: [options.issuer], bearer_methods_supported: ['header'], scopes_supported: ['workspace:read', 'workspace:write'] })); return;
      }
      if (req.url !== resource.pathname) { res.writeHead(404).end(); return; }
      if (req.method !== 'POST') { res.writeHead(405, { Allow: 'POST' }).end(); return; }
      let identity: Identity;
      try { const auth = req.headers.authorization ?? ''; if (!auth.startsWith('Bearer ')) throw new Error('Missing token'); identity = await verifier.verify(auth.slice(7)); }
      catch { res.writeHead(401, { 'WWW-Authenticate': `Bearer scope="workspace:read", resource_metadata="${metadataUrl}"` }).end(); return; }
      if (!identity.scopes.includes('workspace:read')) { res.writeHead(403, { 'WWW-Authenticate': `Bearer error="insufficient_scope", scope="workspace:read", resource_metadata="${metadataUrl}"` }).end(); return; }
      if (!limit.allow(identity.subject)) { res.writeHead(429, { 'Retry-After': '60' }).end(); return; }
      const chunks: Buffer[] = []; let size = 0;
      for await (const chunk of req) { size += chunk.length; if (size > 64000) { res.writeHead(413).end(); return; } chunks.push(chunk); }
      const abort = new AbortController(); res.on('close', () => { if (!res.writableFinished) abort.abort(); });
      // Only MCP transport headers cross this boundary, never Authorization/cookies.
      const headers = new Headers();
      for (const [key, value] of Object.entries(req.headers)) if (value && (key.startsWith('mcp-') || ['accept', 'content-type'].includes(key))) headers.set(key, String(value));
      await context.run(identity, async () => {
        const payload = JSON.parse(Buffer.concat(chunks).toString());
        if (payload.method === 'tools/call' && !identity.scopes.includes('workspace:write')) {
          const requested = (await workspace.gateway.host.catalog()).find(t => t.name === payload.params?.name);
          if (requested && requested.annotations?.readOnlyHint !== true) {
            res.writeHead(403, { 'WWW-Authenticate': `Bearer error="insufficient_scope", scope="workspace:read workspace:write", resource_metadata="${metadataUrl}"` }).end(); return;
          }
        }
        const response = await handler.fetch(new Request(options.resource, { method: 'POST', headers, body: Buffer.concat(chunks), signal: abort.signal }));
        res.writeHead(response.status, Object.fromEntries(response.headers));
        if (response.body) {
          const reader = response.body.getReader();
          try { while (!abort.signal.aborted) { const part = await reader.read(); if (part.done) break; if (!res.write(part.value)) await once(res, 'drain', { signal: abort.signal }); } }
          finally { await reader.cancel(); }
        }
        res.end();
      });
    } catch { if (!res.headersSent) res.writeHead(500); res.end(); }
  });
  server.requestTimeout = 15000; server.headersTimeout = 10000;
  const close = async () => { server.closeAllConnections(); await new Promise<void>(resolve => server.close(() => resolve())); await handler.close(); await workspace.close(); };
  try { server.listen(options.port ?? 8000, options.bind ?? '127.0.0.1'); await once(server, 'listening'); }
  catch (error) { await close(); throw error; }
  return { server, workspace, close };
}
