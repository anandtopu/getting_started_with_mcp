/** Fixed stdio profiles used only by the native deployed gateway. */
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import type { McpServer } from '@modelcontextprotocol/server';
import { notesServer } from '../common/typescript/notes.ts';
import { wikiServer } from '../common/typescript/wiki.ts';
import { remoteWorkspace } from '../common/typescript/remote.ts';
import { realDataServer, startInternalAPI } from '../common/typescript/real_data.ts';
import { workflowServer } from '../common/typescript/workflow.ts';
const profile = process.argv[2];
let factory: () => McpServer; let dispose: () => void | Promise<void> = () => {};
if (profile === 'notes') factory = notesServer;
else if (profile === 'wiki') factory = wikiServer;
else if (profile === 'workflow') factory = workflowServer;
else if (profile === 'issues') { const workspace = remoteWorkspace(); factory = workspace.factory; dispose = workspace.close; }
else if (profile === 'analytics') { const api = await startInternalAPI(); factory = () => realDataServer(api.origin); dispose = api.close; }
else throw new Error('Unknown native service profile');
const handle = serveStdio(factory); let closed = false;
const close = async () => { if (closed) return; closed = true; await handle.close(); await dispose(); };
process.stdin.once('end', () => { void close(); });
for (const event of ['SIGTERM', 'SIGINT'] as const) process.once(event, () => { void close(); });
