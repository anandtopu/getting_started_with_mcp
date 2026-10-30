/** Framework integration: agents.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/15_agent_frameworks/typescript/examples/01_agents.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 15, example: 1, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(15,1));
