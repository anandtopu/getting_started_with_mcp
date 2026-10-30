/** 25-tool endpoint mirror.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/14_tool_design/typescript/examples/01_endpoint_mirror.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 14, example: 1, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(14,1));
