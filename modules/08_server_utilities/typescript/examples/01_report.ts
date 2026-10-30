/** report progress.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/08_server_utilities/typescript/examples/01_report.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 8, example: 1, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(8,1));
