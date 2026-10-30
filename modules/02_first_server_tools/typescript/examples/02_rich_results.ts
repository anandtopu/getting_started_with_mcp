/** Serve structured results and multimedia.
 * Run: npm exec tsx -- modules/02_first_server_tools/typescript/examples/02_rich_results.ts
 * Expected: release_summary and review_assets tools. Spec/capture: ../../README.md and scripts/tier1.py.
 */

import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { richServer } from '../../../../common/typescript/rich.ts';
serveStdio(richServer);
