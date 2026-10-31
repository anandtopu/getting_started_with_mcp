/** controlled retrieval evaluation.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/14_tool_design/typescript/examples/03_evaluation.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: six completed cases per catalog; --live opts into a configured model.
 */
import { parseArgs } from 'node:util';
import { existsSync } from 'node:fs';
import { designEvaluation } from '../../../../common/typescript/tool_design.ts';

if(existsSync('.env'))process.loadEnvFile('.env');
const {values}=parseArgs({options:{live:{type:'boolean',default:false},limit:{type:'string',default:'6'}}});
console.log(JSON.stringify(await designEvaluation({live:values.live,limit:Number(values.limit)}),null,2));
