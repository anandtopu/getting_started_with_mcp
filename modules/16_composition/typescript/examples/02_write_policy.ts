/** Composition: write_policy.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/16_composition/typescript/examples/02_write_policy.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 16, example: 2, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(16,2));
