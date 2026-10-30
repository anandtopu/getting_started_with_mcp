/** Read static text and binary resources.
 * Run: npm exec tsx -- modules/03_resources/typescript/examples/01_static_resources.ts
 * Expected: text/plain and application/pdf. Spec/capture: ../../README.md and scripts/tier1.py.
 */

import { inMemory } from '../../../../common/typescript/clients.ts';
import { wikiServer } from '../../../../common/typescript/wiki.ts';
await inMemory(wikiServer, async client => {
  console.log((await client.listResources()).resources.map(r => r.uri));
  for (const uri of ['wiki://index', 'lumen://contract/1']) {
    const content = (await client.readResource({ uri })).contents[0];
    console.log(content.mimeType, ('text' in content ? String(content.text) : String(content.blob)).length);
  }
});
