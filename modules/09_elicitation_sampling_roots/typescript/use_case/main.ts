/** Use input_required form retries and bind opaque one-use state to exact arguments. Run: node --import tsx modules/09_elicitation_sampling_roots/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(9,part));
