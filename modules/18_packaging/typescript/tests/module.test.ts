import { test, expect } from 'vitest';
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
test('read-only configuration removes write tools', async()=>{expect((await lesson(18,1)).status).toBe('PASS');});
test.each([2,3])('build and launch artifact: example %s', async part=>{
  const result=await lesson(18,part);
  expect(result).toMatchObject({status:'PASS',kind:part===2?'npm':'mcpb',version:'1.0.0',outside_checkout:true,tools:['search_notes'],matches:1});
  expect('files' in result && result.files).toEqual(part===2?
    ['LICENSE','README.md','dist/THIRD_PARTY_LICENSES.txt','dist/cli.cjs','package.json']:
    ['LICENSE','THIRD_PARTY_LICENSES.txt','manifest.json','server/cli.cjs']);
},120000);
