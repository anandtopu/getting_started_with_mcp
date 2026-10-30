/** traces, HTTP load and evaluation.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/13_testing_observability/typescript/examples/03_traces_load_eval.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 13, example: 3, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(13,3));
