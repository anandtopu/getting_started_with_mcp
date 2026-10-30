/** Quality and evaluation: negative.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/13_testing_observability/typescript/examples/02_negative.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 13, example: 2, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(13,2));
