/** Native application services. Each owner closes every SDK handle and database. */
import { InMemoryTransport, type Client } from '@modelcontextprotocol/client';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';
import type { McpServer } from '@modelcontextprotocol/server';
import { DatabaseSync } from 'node:sqlite';
import { resolve } from 'node:path';
import { readFileSync } from 'node:fs';
import { z } from 'zod';
import { newClient } from './clients.ts';
import { notesServer, read, structured } from './notes.ts';
import { wikiServer } from './wiki.ts';
import { remoteWorkspace } from './remote.ts';
import { workflowServer } from './workflow.ts';
import { realDataServer, startInternalAPI } from './real_data.ts';
import { Gateway, type Identity } from './gateway.ts';
import { root } from './data.ts';

export const appUri = 'ui://lumen/analytics.html';
export const appHtml = () => readFileSync(resolve(root, 'modules/17_extensions/ui/dashboard.html'), 'utf8');
export function dashboard() {
  const db = new DatabaseSync(resolve(root, 'data/issues.db'), { readOnly: true });
  try {
    const counts = db.prepare('SELECT status, count(*) AS count FROM issues GROUP BY status ORDER BY status').all();
    return structured({ total: counts.reduce((n, row) => n + Number(row.count), 0), counts });
  } finally { db.close(); }
}
export function addDashboard(server: McpServer) {
  server.registerTool('analytics_dashboard', { description: 'Read synthetic issue counts in an optional sandboxed App.', inputSchema: z.object({}).strict(), annotations: read,
    _meta: { ui: { resourceUri: appUri } } }, dashboard);
  server.registerResource('analytics', appUri, { mimeType: 'text/html;profile=mcp-app' }, () => ({ contents: [{ uri: appUri, mimeType: 'text/html;profile=mcp-app', text: appHtml(), _meta: { ui: { csp: { connectDomains: [], resourceDomains: [], frameDomains: [], baseUriDomains: [] }, permissions: {} } } }] }));
}
export async function localClient(factory: () => McpServer) {
  const [left, right] = InMemoryTransport.createLinkedPair();
  const handle = serveStdio(factory, { transport: left });
  const client = newClient();
  try { await client.connect(right); await client.discover(); }
  catch (error) { await client.close(); await handle.close(); throw error; }
  return { client, close: async () => { await client.close(); await handle.close(); } };
}
export async function nativeWorkspace(identity: () => Identity, mode: 'memory' | 'stdio' = 'memory') {
  const issues = mode === 'memory' ? remoteWorkspace() : undefined;
  let api: Awaited<ReturnType<typeof startInternalAPI>> | undefined;
  const owned: Awaited<ReturnType<typeof localClient>>[] = [];
  const clients = new Map<string, Client>();
  const close = async () => { await Promise.allSettled(owned.map(c => c.close())); await api?.close(); issues?.close(); };
  try {
    if (mode === 'memory') api = await startInternalAPI();
    for (const [alias, factory] of Object.entries({ notes: notesServer, wiki: wikiServer, issues: () => issues!.factory(), analytics: () => realDataServer(api!.origin), workflow: workflowServer })) {
      let connection: Awaited<ReturnType<typeof localClient>>;
      if (mode === 'stdio') {
        const client = newClient(); connection = { client, close: () => client.close() }; owned.push(connection);
        // Explicit child environment: gateway bearer tokens and model keys never
        // enter an upstream's process environment or request headers.
        const env = Object.fromEntries(['PATH', 'Path', 'SystemRoot', 'WINDIR', 'TEMP', 'TMP', 'HOME'].flatMap(name => process.env[name] ? [[name, process.env[name]!]] : []));
        await client.connect(new StdioClientTransport({ command: process.execPath, args: ['--import', 'tsx', resolve(root, 'scripts/typescript_service.ts'), alias], cwd: root, env }), { timeout: 10000 });
        await client.discover();
      } else { connection = await localClient(factory); owned.push(connection); }
      clients.set(alias, connection.client);
    }
    const gateway = new Gateway(clients, identity);
    return { gateway, clients, close, factory: () => gateway.server() };
  } catch (error) { await close(); throw error; }
}
