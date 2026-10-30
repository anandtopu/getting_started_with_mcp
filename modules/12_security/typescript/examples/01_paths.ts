/** Security boundaries: paths.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/12_security/typescript/examples/01_paths.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 12, example: 1, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(12,1));
