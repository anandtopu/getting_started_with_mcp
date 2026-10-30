/** Production hosts: compatibility.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/21_production_hosts/typescript/examples/03_compatibility.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 21, example: 3, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(21,3));
