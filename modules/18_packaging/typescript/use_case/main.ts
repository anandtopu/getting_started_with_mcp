/** Inspect and run the same native notes implementation used by the npm and MCPB packages. Run: node --import tsx modules/18_packaging/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(18,part));
