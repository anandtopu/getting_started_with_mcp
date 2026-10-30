/** List prompts and explicitly choose a release workflow.
 * Run: npm exec tsx -- modules/04_prompts/typescript/examples/01_prompt_arguments.ts
 * Expected: three prompts and real synthetic issue context. Spec/capture: ../../README.md and scripts/tier1.py.
 */

import { inMemory } from '../../../../common/typescript/clients.ts';
import { promptServer } from '../../../../common/typescript/prompts.ts';
await inMemory(promptServer, async client => {
  console.log((await client.listPrompts()).prompts.map(p => p.name));
  console.log(await client.getPrompt({ name: 'release_notes', arguments: { issue_ids: '1,2' } }));
});
