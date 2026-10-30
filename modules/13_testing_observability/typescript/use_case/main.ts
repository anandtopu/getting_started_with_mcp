/** Check actual results, negative cases and the discovered tool inventory within a time budget. Run: node --import tsx modules/13_testing_observability/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(13,part));
