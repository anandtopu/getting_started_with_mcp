/** 03_client_credentials: see B4 README for spec, local fixture and security boundaries.
 * Run: node --import tsx modules/bonus/B4_whats_new/typescript/examples/03_client_credentials.ts
 * Expected: verified result; no connection or activation from card/skill metadata.
 */
import {authFixture} from '../../../../../common/typescript/bonus_fixture.ts';
console.log(authFixture());
