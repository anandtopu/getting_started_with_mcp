/** Fixed profiles: no command strings or remote URLs accepted from a model.
 * Run: node --import tsx modules/bonus/B1_typescript_track/typescript/server.ts notes
 * Inspect/capture: uv run python scripts/phase8.py --capture
 * Expected: JSON-RPC only on stdout.
 */
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { notesServer } from '../../../../common/typescript/notes.ts';
import { workflowServer } from '../../../../common/typescript/workflow.ts';
import { advancedServer } from '../../../../common/typescript/advanced_server.ts';
const profile=process.argv[2]??'notes';
const factory={notes:notesServer,workflow:workflowServer,forms:advancedServer}[profile];
if(!factory) throw new Error('Choose notes, workflow or forms');
serveStdio(factory);
