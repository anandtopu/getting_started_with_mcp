/** Registry: required_fields.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/19_registry/typescript/examples/02_required_fields.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 19, example: 2, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(19,2));
