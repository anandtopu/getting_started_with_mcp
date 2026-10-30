/** Authorization: jwt.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/11_authorization/typescript/examples/01_jwt.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 11, example: 1, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(11,1));
