/** bounded REST API.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/07_real_data/typescript/examples/03_rest_wrapper.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 7, example: 3, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(7,3));
