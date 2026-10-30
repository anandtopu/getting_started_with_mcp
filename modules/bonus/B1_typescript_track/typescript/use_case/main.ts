/** Full additional TypeScript track. Expected: 51 PASS cases. */
import {lesson,modules} from '../../../../../common/typescript/advanced_lessons.ts';
for(const module of modules)for(const part of [1,2,3])console.log(await lesson(module,part));
