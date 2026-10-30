/** Six workflow tools over the same synthetic database.
 * Run: node --import tsx modules/14_tool_design/typescript/task_tools_server.ts
 * Expected: protocol-only stdout, six tools.
 * Spec: https://modelcontextprotocol.io/specification/2026-07-28
 * Capture: uv run python scripts/phase8.py --capture
 */
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { taskToolsServer } from '../../../common/typescript/tool_design.ts';
// KEY IDEA: workflow tools expose bounded evidence and actionable failures.
serveStdio(taskToolsServer);
