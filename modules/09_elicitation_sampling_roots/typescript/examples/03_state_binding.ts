/** Interactive input: state_binding.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/09_elicitation_sampling_roots/typescript/examples/03_state_binding.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 9, example: 3, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(9,3));
