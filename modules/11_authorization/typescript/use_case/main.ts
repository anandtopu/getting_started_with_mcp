/** Verify RS256 signatures against a pinned key and bind identity to issuer, audience and expiry. Run: node --import tsx modules/11_authorization/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(11,part));
