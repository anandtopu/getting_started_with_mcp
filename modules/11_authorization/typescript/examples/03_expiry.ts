/** Authorization: expiry.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/11_authorization/typescript/examples/03_expiry.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 11, example: 3, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(11,3));
