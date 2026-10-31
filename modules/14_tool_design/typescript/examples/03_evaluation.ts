/** controlled retrieval evaluation.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/14_tool_design/typescript/examples/03_evaluation.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: six completed cases per catalog; --live opts into a configured model.
 */
import { parseArgs } from 'node:util';
import { existsSync } from 'node:fs';
import { designEvaluation, EvaluationConfigurationError } from '../../../../common/typescript/tool_design.ts';

try {
  let values;
  try {
    if(existsSync('.env'))process.loadEnvFile('.env');
    values=parseArgs({options:{live:{type:'boolean',default:false},limit:{type:'string',default:'6'}}}).values;
  } catch {throw new EvaluationConfigurationError('Check .env access and use --live and/or --limit 1–6.');}
  console.log(JSON.stringify(await designEvaluation({live:values.live,limit:Number(values.limit)}),null,2));
} catch(error) {
  if(!(error instanceof EvaluationConfigurationError))throw error;
  console.error(error.message);process.exitCode=1;
}
