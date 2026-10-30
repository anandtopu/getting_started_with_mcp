/** Interactive input: accept.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/09_elicitation_sampling_roots/typescript/examples/01_accept.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 9, example: 1, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(9,1));
