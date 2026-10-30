/** Traverse real cursor responses, including an empty page.
 * Run: npm exec tsx -- modules/05_first_client/typescript/examples/02_pages_and_errors.ts
 * Expected: Index, Bulletin; invalid cursor rejected. Spec/capture: ../../README.md and scripts/tier1.py.
 */

import { Server, InMemoryTransport } from '@modelcontextprotocol/server';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { newClient, allResources } from '../../../../common/typescript/clients.ts';
const [serverTransport, clientTransport] = InMemoryTransport.createLinkedPair();
const handle = serveStdio(() => {
  const server = new Server({ name: 'Lumen paged catalog', version: '1.0' }, { capabilities: { resources: {} } });
  server.setRequestHandler('resources/list', request => {
    const cursor = request.params?.cursor;
    if (cursor === undefined) return { resources: [{ uri: 'wiki://index', name: 'Index' }], nextCursor: 'middle' };
    if (cursor === 'middle') return { resources: [], nextCursor: 'last' };
    if (cursor === 'last') return { resources: [{ uri: 'lumen://bulletin', name: 'Bulletin' }] };
    throw new Error('Invalid cursor: restart from the first page.');
  });
  return server;
}, { transport: serverTransport });
const client = newClient();
try {
  await client.connect(clientTransport);
  console.log((await allResources(client)).map(r => r.name));
  try { await client.listResources({ cursor: 'not-a-cursor' }); }
  catch { console.log('Invalid cursor rejected; restart pagination.'); }
} finally { await client.close(); await handle.close(); }
