/** Environment and first contact: versions.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/00_setup/typescript/examples/02_versions.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 0, example: 2, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(0,2));
