/** Persist task state, answer report input and exercise the official App bridge lifecycle. Run: node --import tsx modules/17_extensions/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(17,part));
