/** Own the lifetime of each subprocess connection.
 * Run: npm exec tsx -- modules/05_first_client/typescript/examples/01_stdio_client.ts
 * Expected: note, wiki index, release prompt. Spec/capture: ../../README.md and scripts/tier1.py.
 */

import { withServer } from '../../../../common/typescript/clients.ts';
await withServer('02_first_server_tools', async notes => {
  if (!notes.getServerCapabilities()?.tools) throw new Error('Expected tools capability is unavailable.');
  console.log(await notes.callTool({ name: 'search_notes', arguments: { query: 'release' } }));
});
await withServer('03_resources', async wiki => { console.log(await wiki.readResource({ uri: 'wiki://index' })); });
await withServer('04_prompts', async prompts => { console.log(await prompts.getPrompt({ name: 'release_notes', arguments: { issue_ids: '1' } })); });
