/** Packaging: readonly.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/18_packaging/typescript/examples/01_readonly.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 18, example: 1, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(18,1));
