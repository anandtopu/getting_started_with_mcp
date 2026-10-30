/** 02_server_cards: see B4 README for spec, local fixture and security boundaries.
 * Run: node --import tsx modules/bonus/B4_whats_new/typescript/examples/02_server_cards.ts
 * Expected: verified result; no connection or activation from card/skill metadata.
 */
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {cardBase,validateCard} from '../../../../../common/typescript/server_cards.ts';
console.log(validateCard(JSON.parse(readFileSync(resolve(cardBase,'server-card.json'),'utf8')),'ops.lumen.example'));
