/** Own child connections, bound retries and require reviewed catalogs after discovery. Run: node --import tsx modules/21_production_hosts/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(21,part));
