/** Deliberately awkward 25-tool endpoint catalog.
 * Run: node --import tsx modules/14_tool_design/typescript/mirror_server.ts
 * Expected: protocol-only stdout, 25 tools.
 * Spec: https://modelcontextprotocol.io/specification/2026-07-28
 * Capture: uv run python scripts/phase8.py --capture
 */
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { mirrorServer } from '../../../common/typescript/tool_design.ts';
// KEY IDEA: a large endpoint inventory creates more selection work.
serveStdio(mirrorServer);
