/** Protocol architecture: jsonrpc.
 * Concepts/spec: ../README.md; https://modelcontextprotocol.io/specification/2026-07-28
 * Run: node --import tsx modules/01_architecture_wire/typescript/examples/01_jsonrpc.ts
 * Capture: uv run python scripts/phase8.py --capture
 * Expected: { module: 1, example: 1, status: 'PASS' }.
 */
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
console.log(await lesson(1,1));
