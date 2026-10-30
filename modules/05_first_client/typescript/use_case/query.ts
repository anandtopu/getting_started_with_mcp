import { withServer } from '../../../../common/typescript/clients.ts';
import { parseArgs } from 'node:util';
export async function query(value: string, space = 'engineering', page = 'page-01', watchOnce = false): Promise<void> {
  await withServer('02_first_server_tools', async notes => {
    console.log(await notes.callTool({ name: 'search_notes', arguments: { query: value } }));
  });
  await withServer('03_resources', async wiki => {
    console.log(await wiki.readResource({ uri: `wiki://${space}/${page}` }));
    if (watchOnce) {
      const cache = new Map([['lumen://bulletin', await wiki.readResource({ uri: 'lumen://bulletin' })]]);
      let notify: () => void = () => {};
      const changed = new Promise<void>(resolve => { notify = resolve; });
      wiki.setNotificationHandler('notifications/resources/updated', event => {
        cache.delete(event.params.uri); notify();
      });
      const subscription = await wiki.listen({ resourceSubscriptions: ['lumen://bulletin'] });
      try {
        await wiki.callTool({ name: 'update_bulletin', arguments: { text: 'CLI review complete', confirmed: true } });
        await Promise.race([changed, new Promise((_, reject) => {
          const timer = setTimeout(() => reject(new Error('Notification timeout')), 5000); timer.unref();
        })]);
        cache.set('lumen://bulletin', await wiki.readResource({ uri: 'lumen://bulletin' }));
        console.log('Refetched:', cache.get('lumen://bulletin'));
      } finally { await subscription.close(); }
    }
  });
}
export async function main(): Promise<void> {
  const { values } = parseArgs({ options: { query: { type: 'string', default: 'release' },
    space: { type: 'string', default: 'engineering' }, page: { type: 'string', default: 'page-01' },
    'watch-once': { type: 'boolean', default: false }, 'confirm-demo-write': { type: 'boolean', default: false } } });
  if (values['watch-once'] && !values['confirm-demo-write']) {
    console.error('Review the demo write, then add --confirm-demo-write to approve it.');
    process.exitCode = 1; return;
  }
  await query(values.query, values.space, values.page, values['watch-once']);
}
