/** Run a cancellable report and reject data beyond the documented size limit. Run: node --import tsx modules/08_server_utilities/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(8,part));
