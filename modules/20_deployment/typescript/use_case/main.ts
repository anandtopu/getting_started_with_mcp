/** Test actual HTTP headers and enforce transport and rate policies. Run: node --import tsx modules/20_deployment/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(20,part));
