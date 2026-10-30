/** Open a subscription before changing a resource.
 * Run: npm exec tsx -- modules/03_resources/typescript/examples/03_resource_changes.ts
 * Expected: resource update and Review complete. Spec/capture: ../../README.md and scripts/tier1.py.
 */


import { withServer } from '../../../../common/typescript/clients.ts';
await withServer('03_resources', async client => {
  let notify: () => void = () => {};
  const changed = new Promise<void>(resolve => { notify = resolve; });
  client.setNotificationHandler('notifications/resources/updated', notification => {
    console.log(notification); notify();
  });
  const subscription = await client.listen({ resourcesListChanged: true, resourceSubscriptions: ['lumen://bulletin'] });
  try {
    await client.callTool({ name: 'update_bulletin', arguments: { text: 'Review complete', confirmed: true } });
    await Promise.race([changed, new Promise((_, reject) => {
      const timer = setTimeout(() => reject(new Error('Notification timeout')), 5000); timer.unref();
    })]);
    console.log(await client.readResource({ uri: 'lumen://bulletin' }));
  } finally { await subscription.close(); }
});
