import { McpServer } from '@modelcontextprotocol/server';
import { z } from 'zod';
import { read, structured } from './notes.ts';

const png = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=';
function silence(): string {
  const wav = Buffer.alloc(204);
  wav.write('RIFF'); wav.writeUInt32LE(196, 4); wav.write('WAVEfmt ', 8);
  wav.writeUInt32LE(16, 16); wav.writeUInt16LE(1, 20); wav.writeUInt16LE(1, 22);
  wav.writeUInt32LE(8000, 24); wav.writeUInt32LE(16000, 28);
  wav.writeUInt16LE(2, 32); wav.writeUInt16LE(16, 34); wav.write('data', 36); wav.writeUInt32LE(160, 40);
  return wav.toString('base64');
}
export function richServer(): McpServer {
  const server = new McpServer({ name: 'Lumen rich results', version: '1.0' });
  server.registerTool('release_summary', {
    title: 'Release summary', description: 'Return a structured release summary; negative counts fail output validation.',
    inputSchema: z.object({ open_issues: z.number().int().default(3) }),
    outputSchema: z.object({ title: z.string(), open_issues: z.number().int().min(0) }), annotations: read,
  }, ({ open_issues }) => structured({ title: 'Lumen release review', open_issues }));
  server.registerTool('review_assets', {
    description: 'Return a tiny preview, silent audio fixture, embedded note and wiki link.', annotations: read,
    inputSchema: z.object({}),
  }, () => ({ content: [
    { type: 'image', mimeType: 'image/png', data: png, annotations: { audience: ['user'], priority: 0.5 } },
    { type: 'audio', mimeType: 'audio/wav', data: silence() },
    { type: 'resource', resource: { uri: 'lumen://review/note', mimeType: 'text/plain', text: 'Synthetic review fixture.' } },
    { type: 'resource_link', uri: 'wiki://engineering/page-01', name: 'Release reference', mimeType: 'text/markdown' },
  ] }));
  return server;
}
