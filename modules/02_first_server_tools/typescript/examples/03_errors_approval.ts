/** Keep rejected writes out of the notes array.
 * Run: npm exec tsx -- modules/02_first_server_tools/typescript/examples/03_errors_approval.ts
 * Expected: true, id 2, true. Spec/capture: ../../README.md and scripts/tier1.py.
 */

import { inMemory } from '../../../../common/typescript/clients.ts';
import { notesServer } from '../../../../common/typescript/notes.ts';
await inMemory(notesServer, async client => {
  const args = { title: 'Handover', body: 'Check the release wiki.' };
  console.log('Without approval:', (await client.callTool({ name: 'create_note', arguments: args })).isError);
  console.log('Approved:', (await client.callTool({ name: 'create_note', arguments: { ...args, confirmed: true } })).structuredContent);
  console.log('Invalid title:', (await client.callTool({ name: 'create_note', arguments: { title: '', body: 'x', confirmed: true } })).isError);
});
