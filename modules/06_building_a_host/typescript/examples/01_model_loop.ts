/** Build a host: model_loop.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/06_building_a_host/typescript/examples/01_model_loop.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 6, example: 1, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(6,1));
