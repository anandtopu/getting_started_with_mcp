import { it, expect } from 'vitest';
import { createServer } from 'node:http';
import { generateKeyPairSync, sign } from 'node:crypto';
import { once } from 'node:events';
import { JwksVerifier, oauthGateway } from './gateway_http.ts';
import { newClient } from './clients.ts';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/client';
import { rawHttp } from './http_fixture.ts';

const issuer = 'http://127.0.0.1:8080/realms/lumen'; const resource = 'http://127.0.0.1:8001/mcp';
const key = generateKeyPairSync('rsa', { modulusLength: 2048 }); const other = generateKeyPairSync('rsa', { modulusLength: 2048 });
function token(overrides: Record<string, unknown> = {}, privateKey = key.privateKey, kid = 'primary') {
  const now = Math.floor(Date.now() / 1000);
  const segments = [Buffer.from(JSON.stringify({ alg: 'RS256', kid })).toString('base64url'), Buffer.from(JSON.stringify({ iss: issuer, aud: resource, sub: 'reader', exp: now + 120, iat: now, scope: 'workspace:read', ...overrides })).toString('base64url')];
  const data = segments.join('.'); return data + '.' + sign('RSA-SHA256', Buffer.from(data), privateKey).toString('base64url');
}
it('verifies signatures, exact issuer/resource, expiry, future claims and bounded JWKS retrieval', async () => {
  let fetches = 0;
  const fetcher: typeof fetch = async (_url, options) => { fetches++; expect(options?.redirect).toBe('error'); return Response.json({ keys: [{ ...key.publicKey.export({ format: 'jwk' }), kid: 'primary', alg: 'RS256', use: 'sig' }, { kty: 'RSA', kid: 'encryption', alg: 'RSA-OAEP', use: 'enc' }] }); };
  const verifier = new JwksVerifier(issuer, resource, issuer + '/certs', fetcher);
  expect((await verifier.verify(token({ aud: ['extra', resource] }))).subject).toBe('reader');
  for (const claims of [{ aud: 'https://wrong.example/mcp' }, { iss: 'https://wrong.example' }, { exp: 1 }, { iat: Date.now() / 1000 + 500 }, { nbf: Date.now() / 1000 + 500 }]) await expect(verifier.verify(token(claims))).rejects.toThrow();
  await expect(verifier.verify(token({}, other.privateKey))).rejects.toThrow('signature');
  await expect(verifier.verify(token({}, key.privateKey, 'missing'))).rejects.toThrow('cooling down'); expect(fetches).toBe(1);
  await expect(verifier.verify('x'.repeat(16001))).rejects.toThrow('Invalid token');
  await expect(new JwksVerifier(issuer, resource, issuer + '/certs', async () => new Response('x'.repeat(64001))).verify(token())).rejects.toThrow('too large');
});

it('serves real SDK HTTP requests with concurrent identity/scope isolation, step-up and redacted audit', async () => {
  let keyFetches = 0;
  const jwks = createServer((_req, res) => { keyFetches++; res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify({ keys: [{ ...key.publicKey.export({ format: 'jwk' }), kid: 'primary' }] })); });
  jwks.listen(0, '127.0.0.1'); await once(jwks, 'listening'); const ja = jwks.address(); if (!ja || typeof ja === 'string') throw new Error('No JWKS address');
  const app = await oauthGateway({ issuer, resource, jwksUrl: `http://127.0.0.1:${ja.port}/certs`, port: 0, upstreamMode: 'stdio' }); const address = app.server.address(); if (!address || typeof address === 'string') throw new Error('No gateway address'); const url = `http://127.0.0.1:${address.port}`;
  const reader = newClient(); const writer = newClient();
  const readToken = token(); const writeToken = token({ sub: 'writer', scope: 'workspace:read workspace:write' });
  const post = (auth?: string, payload: unknown = {}) => rawHttp(url + '/mcp', { method: 'POST', headers: { Host: '127.0.0.1:8001', 'Content-Type': 'application/json', ...(auth ? { Authorization: 'Bearer ' + auth } : {}) }, body: JSON.stringify(payload) });
  try {
    expect((await fetch(url + '/mcp', { method: 'POST' })).status).toBe(421);
    expect((await rawHttp(url + '/mcp', { method: 'POST', headers: { Host: '127.0.0.1:8001', Origin: 'https://evil.example' } })).status).toBe(403);
    const absent = await post(); expect(absent.status).toBe(401); expect(absent.headers.get('www-authenticate')).toContain('/.well-known/oauth-protected-resource/mcp');
    const metadata = await rawHttp(url + '/.well-known/oauth-protected-resource/mcp', { headers: { Host: '127.0.0.1:8001' } }); expect((await metadata.json()).authorization_servers).toEqual([issuer]);
    expect((await post(token({ scope: '' }))).status).toBe(403); expect((await post(token({ aud: 'other' }))).status).toBe(401);
    const makeTransport = (value: string) => new StreamableHTTPClientTransport(new URL(url + '/mcp'), { fetch: rawHttp, requestInit: { headers: { Host: '127.0.0.1:8001', Authorization: 'Bearer ' + value } } });
    await Promise.all([reader.connect(makeTransport(readToken)), writer.connect(makeTransport(writeToken))]);
    for (let i = 0; i < 3; i++) {
      const [a, b] = await Promise.all([reader.listTools(undefined, { cacheMode: 'refresh' }), writer.listTools(undefined, { cacheMode: 'refresh' })]);
      expect(a.tools.some(t => t.name === 'notes__create_note')).toBe(false); expect(b.tools.some(t => t.name === 'notes__create_note')).toBe(true);
      for (const alias of ['notes', 'wiki', 'issues', 'analytics', 'workflow']) expect(a.tools.some(t => t.name.startsWith(alias + '__'))).toBe(true);
    }
    const step = await post(readToken, { method: 'tools/call', params: { name: 'notes__create_note' } }); expect(step.status).toBe(403); expect(step.headers.get('www-authenticate')).toContain('workspace:write');
    const [a, b] = await Promise.all([reader.callTool({ name: 'issues__read_issue', arguments: { issue_id: 1 } }), writer.callTool({ name: 'notes__create_note', arguments: { title: 'approved', body: 'synthetic-secret-body', confirmed: true } })]);
    expect(a.isError).not.toBe(true); expect(b.isError).not.toBe(true);
    expect((await reader.callTool({ name: 'analytics__project_details', arguments: { project_id: 1 } })).structuredContent).toMatchObject({ id: 1 });
    await expect(writer.callTool({ name: 'notes__create_note', arguments: { title: 'x', body: 'x' } })).rejects.toThrow('Confirmation');
    expect(app.workspace.gateway.audit).toEqual(expect.arrayContaining([expect.objectContaining({ subject: 'reader', tool: 'issues__read_issue', outcome: 'allowed' }), expect.objectContaining({ subject: 'writer', tool: 'notes__create_note', outcome: 'allowed' })]));
    expect(JSON.stringify(app.workspace.gateway.audit)).not.toContain('synthetic-secret'); expect(JSON.stringify(app.workspace.gateway.audit)).not.toContain(readToken); expect(keyFetches).toBe(1);
  } finally { await reader.close(); await writer.close(); await app.close(); jwks.closeAllConnections(); await new Promise<void>(r => jwks.close(() => r())); }
}, 30000);
