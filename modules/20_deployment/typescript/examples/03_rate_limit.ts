/** Remote deployment: rate_limit.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/20_deployment/typescript/examples/03_rate_limit.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 20, example: 3, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(20,3));
