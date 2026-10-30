/** Measure catalog size and detect changed semantics before execution. Run: node --import tsx modules/14_tool_design/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(14,part));
