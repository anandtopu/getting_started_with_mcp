/** Preserve embedded resource content in a multi-message prompt.
 * Run: npm exec tsx -- modules/04_prompts/typescript/examples/02_embedded_context.ts
 * Expected: user text, user resource and meeting prompt. Spec/capture: ../../README.md and scripts/tier1.py.
 */

import { inMemory } from '../../../../common/typescript/clients.ts';
import { promptServer } from '../../../../common/typescript/prompts.ts';
await inMemory(promptServer, async client => {
  const result = await client.getPrompt({ name: 'summarize_incident', arguments: { space: 'incident_postmortems', page: 'page-01' } });
  for (const message of result.messages) console.log(message.role, message.content.type);
  console.log(await client.getPrompt({ name: 'prepare_meeting', arguments: { customer_id: '1' } }));
});
