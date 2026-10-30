import { expect, test } from 'vitest';
import { App } from '@modelcontextprotocol/ext-apps';
import { AppBridge } from '@modelcontextprotocol/ext-apps/app-bridge';
import { InMemoryTransport } from '@modelcontextprotocol/client';
type CallToolResult = Parameters<AppBridge['sendToolResult']>[0];

test('official App bridge initializes, receives data, refreshes and tears down', async () => {
  const app = new App({ name: 'Lumen analytics', version: '1.0' }, {}, { autoResize: false });
  const host = new AppBridge(null, { name: 'Lumen test host', version: '1.0' }, { serverTools: {} });
  const result: CallToolResult = { content: [{ type: 'text', text: '400 items' }],
    structuredContent: { total: 400, counts: [{ status: 'open', count: 133 }] } };
  host.oncalltool = async params => {
    if (params.name !== 'analytics_dashboard') throw new Error('Tool not allowed');
    return result;
  };
  let received: unknown;
  let tornDown = false;
  app.ontoolresult = value => { received = value; };
  app.onteardown = async () => { tornDown = true; return {}; };
  const [left, right] = InMemoryTransport.createLinkedPair();
  try {
    await host.connect(left);
    await app.connect(right);
    await host.sendToolInput({ arguments: {} });
    await host.sendToolResult(result);
    await expect.poll(() => received).toEqual(result);
    expect(await app.callServerTool({ name: 'analytics_dashboard', arguments: {} })).toEqual(result);
    await expect(app.callServerTool({ name: 'notes__create_note', arguments: {} })).rejects.toThrow();
    await host.teardownResource({});
    expect(tornDown).toBe(true);
  } finally {
    await app.close();
    await host.close();
  }
});
