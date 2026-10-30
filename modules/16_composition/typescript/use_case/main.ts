/** Apply per-user discovery, call-time scope checks, rate limits and bounded audit records. Run: node --import tsx modules/16_composition/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(16,part));
