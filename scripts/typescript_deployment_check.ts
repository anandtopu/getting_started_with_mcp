/** Real Keycloak PKCE/scope step-up and native deployed gateway/Chat Pro acceptance.
 * Requires deployment/typescript/compose.yaml and Playwright Chromium; no Python.
 */
import { strict as assert } from 'node:assert';
import { randomBytes } from 'node:crypto';
import { setTimeout as pause } from 'node:timers/promises';
import { chromium } from '@playwright/test';
import { StreamableHTTPClientTransport, type OAuthClientProvider, type OAuthClientInformationContext, type StoredOAuthTokens } from '@modelcontextprotocol/client';
import { callback, callbackParams } from '../common/typescript/oauth.ts';
import { JwksVerifier } from '../common/typescript/gateway_http.ts';
import { newClient } from '../common/typescript/clients.ts';
import { chatPro } from '../common/typescript/chat_pro.ts';

const issuer = 'http://127.0.0.1:8080/realms/lumen';
const resource = 'http://127.0.0.1:8001/mcp';
for (let attempt = 0; ; attempt++) {
  try { const r = await fetch(issuer + '/.well-known/openid-configuration', { signal: AbortSignal.timeout(2000) }); assert.equal(r.status, 200); break; }
  catch { if (attempt >= 120) throw new Error('Keycloak did not become ready'); await pause(1000); }
}
const verifier = new JwksVerifier(issuer, resource, issuer + '/protocol/openid-connect/certs');
const browser = await chromium.launch(); const context = await browser.newContext(); const page = await context.newPage();
class Provider implements OAuthClientProvider {
  redirectUrl = callback;
  clientMetadata = { redirect_uris: [callback], token_endpoint_auth_method: 'none', grant_types: ['authorization_code'], response_types: ['code'], scope: 'workspace:read' };
  saved?: StoredOAuthTokens; params?: URLSearchParams; private code = ''; private nonce = '';
  bind(c?: OAuthClientInformationContext) { if (c && c.issuer !== issuer) throw new Error('Unreviewed issuer'); }
  clientInformation(c?: OAuthClientInformationContext) { this.bind(c); return { client_id: 'lumen-chat', issuer }; }
  tokens(c?: OAuthClientInformationContext) { this.bind(c); return this.saved; }
  async saveTokens(tokens: StoredOAuthTokens, c?: OAuthClientInformationContext) { this.bind(c); await verifier.verify(tokens.access_token); this.saved = tokens; }
  state() { this.nonce = randomBytes(24).toString('base64url'); return this.nonce; }
  saveCodeVerifier(value: string) { this.code = value; }
  codeVerifier() { return this.code; }
  async redirectToAuthorization(url: URL) {
    assert.equal(url.origin + url.pathname, issuer + '/protocol/openid-connect/auth');
    assert.equal(url.searchParams.get('resource'), resource); assert.equal(url.searchParams.get('code_challenge_method'), 'S256');
    const captured = new Promise<string>(resolve => {
      void page.route(callback + '*', async route => { resolve(route.request().url()); await route.fulfill({ body: 'Authorized synthetic fixture.' }); });
    });
    await page.goto(url.href);
    if (await page.locator('#username').isVisible()) {
      await page.locator('#username').fill('learner'); await page.locator('#password').fill('lumen-local-only'); await page.locator('#kc-login').click();
    }
    this.params = callbackParams(await Promise.race([captured, pause(15000).then(() => { throw new Error('Authorization callback timed out'); })]), this.nonce, issuer);
    await page.unroute(callback + '*');
  }
}
const provider = new Provider(); const transport = new StreamableHTTPClientTransport(new URL(resource), { authProvider: provider });
let client = newClient();
try {
  assert.equal((await fetch(resource, { method: 'POST' })).status, 401);
  try { await client.connect(transport); await client.discover(); } catch { assert.ok(provider.params, 'SDK should request PKCE authorization'); }
  assert.ok(provider.params); await transport.finishAuth(provider.params); provider.params = undefined;
  await client.close(); client = newClient();
  const authenticated = new StreamableHTTPClientTransport(new URL(resource), { authProvider: provider }); await client.connect(authenticated); await client.discover();
  const initial = await verifier.verify(provider.saved!.access_token); assert.deepEqual(initial.scopes, ['workspace:read']);
  const catalog = (await client.listTools()).tools;
  for (const alias of ['notes', 'wiki', 'issues', 'analytics', 'workflow']) assert.ok(catalog.some(t => t.name.startsWith(alias + '__')), alias);
  assert.ok(!catalog.some(t => t.name === 'notes__create_note'));
  assert.equal((await client.callTool({ name: 'issues__read_issue', arguments: { issue_id: 1 } })).isError, undefined);
  assert.equal((await client.callTool({ name: 'workflow__triage_week', arguments: { week_start: '2026-07-13' } })).isError, undefined);
  const proposal = { name: 'notes__create_note', arguments: { title: 'Native deployment acceptance', body: 'Synthetic approved write.', confirmed: true } };
  let written;
  try { written = await client.callTool(proposal); } catch { assert.ok(provider.params, 'Missing write scope must trigger step-up'); }
  if (provider.params) { await authenticated.finishAuth(provider.params); provider.params = undefined; written = await client.callTool(proposal); }
  const stepped = await verifier.verify(provider.saved!.access_token); assert.ok(stepped.scopes.includes('workspace:write'));
  assert.ok(written); assert.notEqual(written.isError, true);
  await assert.rejects(new JwksVerifier(issuer, 'https://other.example/mcp', issuer + '/protocol/openid-connect/certs').verify(provider.saved!.access_token));

  // The full native web backend connects to the deployed authenticated gateway.
  process.env.LUMEN_NATIVE_TEST_TOKEN = provider.saved!.access_token;
  const app = await chatPro(0, [{ alias: 'gateway', profile: 'gateway', mode: 'current', url: resource, token_env: 'LUMEN_NATIVE_TEST_TOKEN' }], ':memory:');
  try {
    const address = app.server.address(); assert.ok(address && typeof address === 'object');
    const chat = await context.newPage(); await chat.goto(`http://127.0.0.1:${address.port}`);
    await chat.locator('#status').getByText('Workspace ready', { exact: true }).waitFor();
    await chat.getByLabel('Message', { exact: true }).fill('Read a deployed issue'); await chat.getByRole('button', { name: /Send message/ }).click();
    await chat.getByRole('button', { name: 'Approve once' }).click(); await chat.locator('#status').getByText('complete', { exact: true }).waitFor();
    assert.ok(await chat.locator('#conversation').getByText('Tool evidence', { exact: false }).isVisible());
    const visible = await chat.content(); assert.ok(!visible.includes(provider.saved!.access_token)); await chat.close();
  } finally { await app.close(); delete process.env.LUMEN_NATIVE_TEST_TOKEN; }
  console.log('PASS native deployment: Keycloak PKCE, audience, scope step-up, five upstreams, approved write, Chat Pro remote tool review');
} finally { await client.close(); await context.close(); await browser.close(); }
