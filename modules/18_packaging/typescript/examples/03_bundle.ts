/** Packaging: validate, pack, inspect and launch the MCPB archive outside the checkout.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/18_packaging/typescript/examples/03_bundle.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 18, example: 3, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(18,3));
