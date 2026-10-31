import { it, expect, vi } from 'vitest';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { setTimeout as pause } from 'node:timers/promises';
import { ChatSession, chatPro, fixtureModel } from './chat_pro.ts';
import { hostConfig } from './chat_services.ts';
import { rawHttp } from './http_fixture.ts';

async function pending(session: ChatSession) { for (let i = 0; i < 100; i++) { if (session.pending) return session.pending; await pause(10); } throw new Error('No decision'); }
async function withSession(action: (session: ChatSession) => Promise<void>) { const session = new ChatSession(hostConfig()); try { await session.start(); await action(session); } finally { await session.close(); } }

it('connects an explicitly configured legacy server and refreshes it on reconnect', async () => {
  const session = new ChatSession([{ alias: 'notes', profile: 'notes', mode: 'legacy' }]);
  try { await session.start(); expect(session.connections.get('notes')!.info.protocol).toBe('legacy'); await session.reconnect(); expect((await session.connections.get('notes')!.catalog()).some(t => t.name === 'search_notes')).toBe(true); }
  finally { await session.close(); }
});

it('rejects model confirmation before approval and binds a one-use decision to catalog semantics', async () => {
  await withSession(async session => {
    session.chat('write', async () => ({ calls: [{ name: 'notes__create_note', arguments: { title: 'x', body: 'x', confirmed: true } }] }));
    await session.run; expect(session.status).toBe('error'); expect(session.pending).toBeUndefined();
    session.chat('note', fixtureModel('note')); const decision = await pending(session);
    const connection = session.connections.get('notes')!; const original = connection.catalog.bind(connection);
    vi.spyOn(connection, 'catalog').mockImplementation(async () => (await original()).map(t => ({ ...t, description: 'Changed after review' })));
    const answer = { id: decision.id, action: 'accept' }; session.answer(answer); expect(() => session.answer(answer)).toThrow('already answered');
    await session.run; expect(session.status).toBe('error'); expect(session.events.some(e => e.type === 'tool_result')).toBe(false);
  });
});

it('cancellation prevents a late model response from proposing or executing a tool', async () => {
  await withSession(async session => {
    let release!: () => void; const wait = new Promise<void>(r => { release = r; });
    session.chat('late', async () => { await wait; return { calls: [{ name: 'notes__create_note', arguments: { title: 'late', body: 'late' } }] }; });
    const stopped = session.cancel(); release(); await stopped;
    expect(session.status).toBe('cancelled'); expect(session.pending).toBeUndefined(); expect(session.events.some(e => e.type === 'tool_result')).toBe(false);
  });
});

it('validates form answers, declines ordinary input, and cancels Tasks with no late result', async () => {
  await withSession(async session => {
    session.chat('close', fixtureModel('close')); session.answer({ id: (await pending(session)).id, action: 'accept' });
    await pause(30); const form = await pending(session); expect(form.kind).toBe('input');
    expect(() => session.answer({ id: form.id, action: 'accept', content: { approve: 'yes' } })).toThrow('Invalid input');
    session.answer({ id: form.id, action: 'decline' }); await session.run;
    expect(session.status).toBe('complete'); expect(JSON.stringify(session.events)).toContain('"closed":[]');
    session.chat('report', fixtureModel('report')); session.answer({ id: (await pending(session)).id, action: 'accept' });
    await pause(30); expect((await pending(session)).kind).toBe('input'); await session.cancel();
    expect(session.status).toBe('cancelled'); expect(session.events.filter(e => e.type === 'task').at(-1)?.status).toBe('cancelled');
  });
});

it('enforces browser sessions, CSRF, App allowlist and invalid host/origin boundaries', async () => {
  const app = await chatPro(0, hostConfig(), ':memory:'); const address = app.server.address(); if (!address || typeof address === 'string') throw new Error('No address'); const url = `http://127.0.0.1:${address.port}`;
  try {
    expect((await fetch(url + '/api/session', { method: 'POST' })).status).toBe(403);
    expect((await rawHttp(url, { headers: { Host: 'evil.example' } })).status).toBe(421);
    expect((await fetch(url, { headers: { Origin: 'https://evil.example' } })).status).toBe(403);
    const first = await fetch(url + '/api/session', { method: 'POST', headers: { 'x-lumen-client': 'web' } }); const state = await first.json(); const cookie = first.headers.get('set-cookie')!.split(';')[0];
    const second = await fetch(url + '/api/session', { method: 'POST', headers: { 'x-lumen-client': 'web' } }); const other = await second.json();
    const post = (path: string, value: unknown, csrf = state.csrf) => fetch(url + '/api/' + path, { method: 'POST', headers: { Cookie: cookie, 'x-csrf-token': csrf, 'Content-Type': 'application/json' }, body: JSON.stringify(value) });
    expect((await post('chat', { prompt: 'note' }, other.csrf)).status).toBe(403);
    expect((await post('chat', { prompt: 'dashboard' })).status).toBe(202);
    const session = [...app.sessions.values()][0]; const review = await pending(session);
    const otherSession = [...app.sessions.values()][1]; expect(() => otherSession.answer({ id: review.id, action: 'accept' })).toThrow();
    expect((await post('answer', { id: review.id, action: 'accept' })).status).toBe(200); await session.run;
    expect((await post('app-call', { name: 'create_note', arguments: {} })).status).toBe(400);
    expect((await post('app-call', { name: 'analytics_dashboard', arguments: {} })).status).toBe(200);
    const frame = await fetch(url + '/api/app-view/' + session.app!.id, { headers: { Cookie: cookie } }); expect(frame.headers.get('content-security-policy')).toContain("connect-src 'none'");
    expect((await fetch(url + '/api/app-view/' + session.app!.id, { headers: { Cookie: second.headers.get('set-cookie')!.split(';')[0] } })).status).toBe(404);
    expect((await post('answer', { id: review.id, action: 'accept' })).status).toBe(400);
    expect((await post('close', {})).status).toBe(200); expect((await post('cancel', {})).status).toBe(401);
  } finally { await app.close(); }
});

it('runs an actual provider HTTP conversation through the web API, with separate approval and private configuration', async () => {
  const requests: Record<string, unknown>[] = [];
  const modelServer = createServer(async (req, res) => {
    const chunks: Buffer[] = []; for await (const chunk of req) chunks.push(chunk); requests.push(JSON.parse(Buffer.concat(chunks).toString()));
    res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(requests.length === 1 ? { message: { role: 'assistant', tool_calls: [{ function: { name: 'notes__search_notes', arguments: { query: 'release' } } }] } } : { message: { role: 'assistant', content: 'Read the approved evidence.' } }));
  });
  modelServer.listen(0, '127.0.0.1'); await once(modelServer, 'listening'); const modelAddress = modelServer.address(); if (!modelAddress || typeof modelAddress === 'string') throw new Error('No model address');
  const previous = process.env.OLLAMA_HOST; process.env.OLLAMA_HOST = `http://127.0.0.1:${modelAddress.port}`;
  const app = await chatPro(0, hostConfig(), ':memory:'); const address = app.server.address(); if (!address || typeof address === 'string') throw new Error('No address'); const url = `http://127.0.0.1:${address.port}`;
  try {
    const response = await fetch(url + '/api/session', { method: 'POST', headers: { 'x-lumen-client': 'web' } }); const state = await response.json();
    const headers = { Cookie: response.headers.get('set-cookie')!.split(';')[0], 'x-csrf-token': state.csrf, 'Content-Type': 'application/json' };
    expect((await fetch(url + '/api/chat', { method: 'POST', headers, body: JSON.stringify({ prompt: 'Read release notes', provider: 'ollama', model: 'test-model' }) })).status).toBe(202);
    const session = [...app.sessions.values()][0]; const review = await pending(session); expect(requests).toHaveLength(1);
    expect(JSON.stringify(requests[0].tools)).not.toContain('confirmed');
    await fetch(url + '/api/answer', { method: 'POST', headers, body: JSON.stringify({ id: review.id, action: 'accept' }) }); await session.run;
    expect(session.status).toBe('complete'); expect(requests).toHaveLength(2); expect(JSON.stringify(requests[1])).toContain('Release handover'); expect(JSON.stringify(session.snapshot())).not.toContain(process.env.OLLAMA_HOST);
  } finally { if (previous === undefined) delete process.env.OLLAMA_HOST; else process.env.OLLAMA_HOST = previous; await app.close(); modelServer.closeAllConnections(); await new Promise<void>(r => modelServer.close(() => r())); }
});
