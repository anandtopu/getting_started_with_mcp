/** Test-only HTTP sender that can exercise Host-header attacks (fetch strips Host). */
import { request } from 'node:http';
export const rawHttp: typeof fetch = async (input, init) => {
  const value = new Request(input, init);
  const body = value.body ? Buffer.from(await value.arrayBuffer()) : undefined;
  if (new URL(value.url).hostname !== '127.0.0.1') throw new Error('Loopback fixtures only');
  return new Promise<Response>((resolve, reject) => {
    const req = request(value.url, { method: value.method, headers: Object.fromEntries(value.headers), signal: value.signal }, res => {
      const chunks: Buffer[] = []; let size = 0;
      res.on('data', chunk => { size += chunk.length; if (size > 2000000) req.destroy(new Error('Fixture response too large')); else chunks.push(chunk); });
      res.on('error', reject);
      res.on('end', () => {
        const headers = new Headers(); for (const [key, value] of Object.entries(res.headers)) if (value) headers.set(key, Array.isArray(value) ? value.join(', ') : value);
        resolve(new Response([204, 304].includes(res.statusCode!) ? null : Buffer.concat(chunks), { status: res.statusCode, headers }));
      });
    });
    req.on('error', reject); req.end(body);
  });
};
