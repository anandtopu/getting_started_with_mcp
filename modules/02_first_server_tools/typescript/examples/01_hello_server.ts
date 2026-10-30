/** Register a tool with a Zod object schema.
 * Run: npm exec tsx -- modules/02_first_server_tools/typescript/examples/01_hello_server.ts
 * Expected: protocol only; call welcome in Inspector. Spec/capture: ../../README.md and scripts/tier1.py.
 */

import { McpServer } from '@modelcontextprotocol/server';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { z } from 'zod';
import { read, text } from '../../../../common/typescript/notes.ts';
export function helloServer() {
  const server = new McpServer({ name: 'Lumen hello', version: '1.0' });
  server.registerTool('welcome', { title: 'Welcome a teammate',
    description: 'Welcome a synthetic teammate to Lumen Labs; provide their display name.',
    inputSchema: z.object({ name: z.string().min(1).max(60) }), annotations: read,
  }, ({ name }) => text(`Welcome to Lumen Labs, ${name}!`));
  return server;
}
serveStdio(helloServer);
