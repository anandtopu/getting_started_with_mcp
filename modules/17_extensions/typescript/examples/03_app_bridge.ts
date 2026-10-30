/** Tasks and Apps: app_bridge.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/17_extensions/typescript/examples/03_app_bridge.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 17, example: 3, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(17,3));
