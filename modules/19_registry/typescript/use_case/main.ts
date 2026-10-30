/** Separate namespace/schema validation from permission to connect to a server. Run: node --import tsx modules/19_registry/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(19,part));
