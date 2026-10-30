/** Read SQLite data, reject an unapproved write, and prove replay-safe issue creation. Run: node --import tsx modules/07_real_data/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(7,part));
