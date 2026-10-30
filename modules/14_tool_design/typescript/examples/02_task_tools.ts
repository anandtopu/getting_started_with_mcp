/** six workflow tools.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/14_tool_design/typescript/examples/02_task_tools.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 14, example: 2, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(14,2));
