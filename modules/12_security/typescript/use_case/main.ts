/** Deny path escape, redact nested credentials and reject public cleartext endpoints. Run: node --import tsx modules/12_security/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(12,part));
