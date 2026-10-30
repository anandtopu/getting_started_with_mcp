/** Run the same two-step read-only triage in three actual JavaScript runtimes. Run: node --import tsx modules/15_agent_frameworks/typescript/use_case/main.ts */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
for(const part of [1,2,3]) console.log(await lesson(15,part));
