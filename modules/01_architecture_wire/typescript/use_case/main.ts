/** Send correlated requests over the official transport, then compare raw and SDK paths. Run: node --import tsx modules/01_architecture_wire/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(1,part));
