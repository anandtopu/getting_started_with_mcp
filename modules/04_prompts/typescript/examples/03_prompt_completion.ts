/** Context-sensitive completions and prompt catalog change notifications.
 * Run: npm exec tsx -- modules/04_prompts/typescript/examples/03_prompt_completion.ts
 * Expected: eight suggestions and review_checklist. Spec/capture: ../../README.md and scripts/tier1.py.
 */


import { withServer } from '../../../../common/typescript/clients.ts';
await withServer('04_prompts', async client => {
  const limited = await client.complete({ ref: { type: 'ref/prompt', name: 'release_notes' },
    argument: { name: 'issue_ids', value: '' } });
  console.log('Suggestions/total/hasMore:', limited.completion.values.length, limited.completion.total, limited.completion.hasMore);
  console.log(await client.complete({ ref: { type: 'ref/prompt', name: 'summarize_incident' },
    argument: { name: 'page', value: 'page-0' }, context: { arguments: { space: 'engineering' } } }));
  let notify: () => void = () => {};
  const changed = new Promise<void>(resolve => { notify = resolve; });
  client.setNotificationHandler('notifications/prompts/list_changed', notification => { console.log(notification); notify(); });
  const subscription = await client.listen({ promptsListChanged: true });
  try {
    await client.callTool({ name: 'enable_checklist', arguments: { confirmed: true } });
    await Promise.race([changed, new Promise((_, reject) => {
      const timer = setTimeout(() => reject(new Error('Notification timeout')), 5000); timer.unref();
    })]);
    console.log((await client.listPrompts()).prompts.map(p => p.name));
  } finally { await subscription.close(); }
});
