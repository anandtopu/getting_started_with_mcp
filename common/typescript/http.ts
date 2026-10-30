/** Loopback HTTP adapter with Host/Origin checks and streaming cancellation. */
import { createServer } from 'node:http';
import { once } from 'node:events';
import { createMcpHandler, type McpServer, type ServerEventBus } from '@modelcontextprotocol/server';

export function serveHttp(factory: () => McpServer, port = 8000, bus?: ServerEventBus) {
  const handler = createMcpHandler(factory, { legacy: 'reject', maxRequestBodySize: 64000, bus });
  const server = createServer(async (req, res) => {
    try {
      const address = server.address();
      const actualPort = typeof address === 'object' && address ? address.port : port;
      if (![ `127.0.0.1:${actualPort}`, `localhost:${actualPort}` ].includes(req.headers.host ?? '')) {
        res.writeHead(421).end('Invalid Host'); return;
      }
      if (req.headers.origin && req.headers.origin !== 'http://localhost:3000') {
        res.writeHead(403).end('Invalid Origin'); return;
      }
      if (req.headers.origin) {
        res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000');
        res.setHeader('Vary', 'Origin');
      }
      if (req.method === 'OPTIONS') {
        res.setHeader('Access-Control-Allow-Methods', 'POST');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type, MCP-Protocol-Version, Mcp-Method, Mcp-Name, Mcp-Param-Region');
        res.writeHead(204).end(); return;
      }
      if (req.url !== '/mcp') { res.writeHead(404).end(); return; }
      const abort = new AbortController();
      res.on('close', () => { if (!res.writableFinished) abort.abort(); });
      const chunks: Buffer[] = [];
      let size = 0;
      for await (const chunk of req) {
        size += chunk.length;
        if (size > 64000) { res.writeHead(413).end(); return; }
        chunks.push(chunk);
      }
      const headers = new Headers();
      for (const [key, value] of Object.entries(req.headers)) {
        if (value !== undefined) headers.set(key, Array.isArray(value) ? value.join(', ') : value);
      }
      const response = await handler.fetch(new Request(`http://127.0.0.1:${actualPort}/mcp`, {
        method: req.method, headers, signal: abort.signal,
        body: ['GET', 'HEAD'].includes(req.method ?? '') ? undefined : Buffer.concat(chunks),
      }));
      res.writeHead(response.status, Object.fromEntries(response.headers));
      if (response.body) {
        const reader = response.body.getReader();
        try {
          while (!abort.signal.aborted) {
            const next = await reader.read();
            if (next.done) break;
            if (!res.write(next.value)) await once(res, 'drain', { signal: abort.signal });
          }
        } finally { await reader.cancel(); }
      }
      res.end();
    } catch {
      if (!res.headersSent) res.writeHead(500);
      res.end();
    }
  });
  return { server, handler, start: () => server.listen(port, '127.0.0.1') };
}
