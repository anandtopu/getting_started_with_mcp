import { Client, InMemoryTransport } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import type { McpServer } from '@modelcontextprotocol/server';
import { resolve } from 'node:path';
import { root } from './data.ts';

export function newClient(): Client {
  return new Client({ name: 'Lumen lesson client', version: '1.0' }, {
    versionNegotiation: { mode: { pin: '2026-07-28' } },
  });
}
export async function inMemory<T>(factory: () => McpServer, action: (client: Client) => Promise<T>): Promise<T> {
  const [serverTransport, clientTransport] = InMemoryTransport.createLinkedPair();
  const handle = serveStdio(factory, { transport: serverTransport });
  const client = newClient();
  try { await client.connect(clientTransport); await client.discover(); return await action(client); }
  finally { await client.close(); await handle.close(); }
}
export async function withServer<T>(module: string, action: (client: Client) => Promise<T>): Promise<T> {
  const transport = new StdioClientTransport({ command: process.execPath,
    args: ['--import', 'tsx', resolve(root, `modules/${module}/typescript/use_case/main.ts`)], cwd: root });
  const client = newClient();
  try { await client.connect(transport); await client.discover(); return await action(client); }
  finally { await client.close(); }
}
export async function allResources(client: Client, maxPages = 10) {
  const result = [];
  let cursor: string | undefined;
  const seen = new Set<string>();
  for (let i = 0; i < maxPages; i++) {
    const page = await client.listResources({ cursor });
    result.push(...page.resources);
    cursor = page.nextCursor;
    if (cursor === undefined) return result;
    if (seen.has(cursor)) throw new Error('Repeated cursor: stop instead of looping forever.');
    seen.add(cursor);
  }
  throw new Error('Page budget exceeded.');
}
