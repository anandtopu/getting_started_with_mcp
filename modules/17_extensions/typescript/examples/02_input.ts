/** Tasks and Apps: input.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/17_extensions/typescript/examples/02_input.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 17, example: 2, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(17,2));
