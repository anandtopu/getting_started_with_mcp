/** Discover a URI template and follow a resource link.
 * Run: npm exec tsx -- modules/03_resources/typescript/examples/02_resource_templates.ts
 * Expected: wiki template and engineering page-01. Spec/capture: ../../README.md and scripts/tier1.py.
 */

import { inMemory } from '../../../../common/typescript/clients.ts';
import { wikiServer } from '../../../../common/typescript/wiki.ts';
await inMemory(wikiServer, async client => {
  console.log((await client.listResourceTemplates()).resourceTemplates);
  console.log(await client.complete({ ref: { type: 'ref/resource', uri: 'wiki://{space}/{page}' },
    argument: { name: 'space', value: 'eng' } }));
  const result = await client.callTool({ name: 'find_page', arguments: { space: 'engineering', page: 'page-01' } });
  const link = result.content[0];
  if (link.type !== 'resource_link') throw new Error('Expected resource link');
  console.log(await client.readResource({ uri: link.uri }));
});
