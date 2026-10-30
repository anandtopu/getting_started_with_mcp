/** Real loopback clients; no external API or model needed. */
import { strict as assert } from 'node:assert';
import { once } from 'node:events';
import { request } from 'node:http';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/client';
import { newClient } from './clients.ts';
import { serveHttp } from './http.ts';
import { remoteWorkspace } from './remote.ts';

export async function withRemote(action: (url: URL) => Promise<void>) {
  const workspace = remoteWorkspace();
  const app = serveHttp(workspace.factory, 0, workspace.bus);
  app.start();
  await once(app.server, 'listening');
  const address = app.server.address();
  assert(address && typeof address === 'object');
  try { await action(new URL(`http://127.0.0.1:${address.port}/mcp`)); }
  finally {
    await app.handler.close();
    app.server.closeAllConnections();
    await new Promise<void>((resolve, reject) => app.server.close(error => error ? reject(error) : resolve()));
    workspace.close();
  }
}

export async function headerLab(url: URL) {
  const body = { jsonrpc: '2.0', id: 1, method: 'tools/call', params: {
    name: 'route_region', arguments: { region: 'east' }, _meta: {
      'io.modelcontextprotocol/protocolVersion': '2026-07-28',
      'io.modelcontextprotocol/clientCapabilities': {},
      'io.modelcontextprotocol/clientInfo': { name: 'header-lab', version: '1' },
    },
  } };
  const headers = { 'Content-Type': 'application/json', Accept: 'application/json, text/event-stream',
    'MCP-Protocol-Version': '2026-07-28', 'Mcp-Method': 'tools/call', 'Mcp-Name': 'route_region', 'Mcp-Param-Region': 'east' };
  const cases: [Record<string, string>, number][] = [[{}, 200], [{ Origin: 'https://evil.example' }, 403],
    [{ 'Mcp-Method': 'resources/read' }, 400],
    [{ 'Mcp-Name': 'wrong' }, 400], [{ 'Mcp-Param-Region': 'west' }, 400]];
  for (const [extra, expected] of cases) {
    const response = await fetch(url, { method: 'POST', headers: { ...headers, ...extra }, body: JSON.stringify(body) });
    assert.equal(response.status, expected); await response.text();
  }
  const preflight = await fetch(url, { method: 'OPTIONS', headers: { Origin: 'http://localhost:3000', 'Access-Control-Request-Method': 'POST' } });
  assert.equal(preflight.headers.get('access-control-allow-origin'), 'http://localhost:3000');
  // Fetch may replace Host; use the native client to send the intended bad value.
  const status = await new Promise<number | undefined>((resolve, reject) => {
    const req = request(url, { method: 'POST', headers: { ...headers, Host: 'evil.example' } }, res => {
      res.resume(); res.once('end', () => resolve(res.statusCode));
    });
    req.on('error', reject); req.end(JSON.stringify(body));
  });
  assert.equal(status, 421);
}

export async function recoveryLab(url: URL) {
  const client = newClient();
  try {
    await client.connect(new StreamableHTTPClientTransport(url)); await client.discover();
    await client.listTools();
    const unicode = await client.callTool({ name: 'route_region', arguments: { region: 'Hello, 世界' } });
    assert(!unicode.isError);
    const args = { issue: { title: 'Remote handover' }, operation_key: 'recovery-demo', confirmed: true };
    const first = await client.callTool({ name: 'create_issue', arguments: args });
    const retry = await client.callTool({ name: 'create_issue', arguments: args });
    assert.deepEqual(first.structuredContent, retry.structuredContent);
    for (let i = 0; i < 2; i++) {
      let notify!: () => void;
      const event = new Promise<void>(resolve => { notify = resolve; });
      client.setNotificationHandler('notifications/resources/updated', () => notify());
      const subscription = await client.listen({ resourceSubscriptions: ['workspace://review'] });
      await client.callTool({ name: 'publish_review', arguments: { text: `Review ${i}` } });
      let timer: ReturnType<typeof setTimeout> | undefined;
      try { await Promise.race([event, new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('Missing update')), 3000); })]); }
      finally { clearTimeout(timer); await subscription.close(); }
      const resource = await client.readResource({ uri: 'workspace://review' });
      assert('text' in resource.contents[0]);
      assert.equal(resource.contents[0].text, `Review ${i}`);
    }
  } finally { await client.close(); }
}
