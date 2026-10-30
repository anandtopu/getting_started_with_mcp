import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { McpServer, ResourceTemplate } from '@modelcontextprotocol/server';
import { z } from 'zod';
import { root, safePath } from './data.ts';
import { read, replace, text, failure } from './notes.ts';

export const spaces = ['engineering', 'product', 'hr', 'onboarding', 'incident_postmortems'];
export const pages = Array.from({ length: 8 }, (_, i) => `page-0${i + 1}`);
export function wikiText(space: string, page: string): string {
  if (!spaces.includes(space) || !pages.includes(page)) throw new Error('Unknown wiki page: use a listed space and page-01 through page-08.');
  return readFileSync(safePath(resolve(root, 'data'), `wiki/${space}/${page}.md`), 'utf8');
}
export function wikiServer(): McpServer {
  const server = new McpServer({ name: 'Lumen wiki', version: '2.0' },
    { capabilities: { resources: { subscribe: true, listChanged: true } } });
  let bulletin = 'Release review at 14:00 UTC';
  let revision = 1;
  let statusEnabled = false;
  server.registerResource('index', 'wiki://index', { mimeType: 'text/plain', title: 'Lumen wiki index',
    annotations: { audience: ['user'], priority: 1 } }, uri => ({
    contents: [{ uri: uri.href, mimeType: 'text/plain', text: spaces.join(', ') }],
  }));
  server.registerResource('page', new ResourceTemplate('wiki://{space}/{page}', {
    list: undefined, complete: {
      space: value => spaces.filter(s => s.startsWith(value)),
      page: (value, context) => spaces.includes(context?.arguments?.space ?? '')
        ? pages.filter(p => p.startsWith(value)) : [],
    },
  }),
    { mimeType: 'text/markdown' }, (uri, { space, page }) => ({
      contents: [{ uri: uri.href, mimeType: 'text/markdown', text: wikiText(String(space), String(page)) }],
    }));
  server.registerResource('contract', 'lumen://contract/1', { mimeType: 'application/pdf' }, uri => ({
    contents: [{ uri: uri.href, mimeType: 'application/pdf', blob: readFileSync(resolve(root, 'data/files/contracts/contract-01.pdf')).toString('base64') }],
  }));
  server.registerResource('bulletin', 'lumen://bulletin', { mimeType: 'text/plain' }, uri => ({
    contents: [{ uri: uri.href, mimeType: 'text/plain', text: bulletin }],
  }));
  server.registerTool('find_page', {
    description: 'Return a wiki resource link after checking that the page exists.', annotations: read,
    inputSchema: z.object({ space: z.string().default('engineering'), page: z.string().default('page-01') }),
  }, ({ space, page }) => {
    wikiText(space, page);
    return { content: [{ type: 'resource_link', uri: `wiki://${space}/${page}`, name: page, mimeType: 'text/markdown' }] };
  });
  server.registerTool('update_bulletin', {
    description: 'Update only the in-memory training bulletin after confirmation; notify subscribers.',
    inputSchema: z.object({ text: z.string().min(1).max(500), confirmed: z.boolean().default(false) }), annotations: replace,
  }, async ({ text: value, confirmed }) => {
    if (!confirmed) return failure('Confirmation required: review the bulletin text.');
    bulletin = value;
    revision += 1;
    if (!statusEnabled) {
      server.registerTool('bulletin_status', {
        description: 'Read the revision after the bulletin has been reviewed at least once.',
        inputSchema: z.object({}), annotations: read,
      }, () => text(`Bulletin revision ${revision}`));
      server.registerResource('review_receipt', 'lumen://review-receipt', { mimeType: 'text/plain' }, uri => ({
        contents: [{ uri: uri.href, mimeType: 'text/plain', text: `Reviewed bulletin revision ${revision}` }],
      }));
      statusEnabled = true;
    }
    await server.server.sendResourceUpdated({ uri: 'lumen://bulletin' });
    server.sendResourceListChanged();
    server.sendToolListChanged();
    return text(`Bulletin revision ${revision}`);
  });
  return server;
}
