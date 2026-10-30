/** Read-only named analytics queries over stdio.
 * Run: node --import tsx modules/07_real_data/typescript/analytics_server.ts
 * Expected: protocol-only stdout, analytics_page in tools/list.
 * Spec: https://modelcontextprotocol.io/specification/2026-07-28
 * Capture: uv run python scripts/phase8.py --capture
 */
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { realDataServer } from '../../../common/typescript/real_data.ts';
// KEY IDEA: caller supplies dates and page bounds, never SQL or an arbitrary URL.
serveStdio(() => realDataServer());
