/** Run a bounded model loop; proposals remain separate from human authorization. Run: node --import tsx modules/06_building_a_host/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(6,part));
