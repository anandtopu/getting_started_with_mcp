/** 01_skills: see B4 README for spec, local fixture and security boundaries.
 * Run: node --import tsx modules/bonus/B4_whats_new/typescript/examples/01_skills.ts
 * Expected: verified result; no connection or activation from card/skill metadata.
 */
import {skillsDemo} from '../../../../../common/typescript/skills.ts';
console.log(await skillsDemo());
