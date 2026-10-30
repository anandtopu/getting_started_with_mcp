/** Build a host: provider_shapes.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/06_building_a_host/typescript/examples/03_provider_shapes.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 6, example: 3, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(6,3));
