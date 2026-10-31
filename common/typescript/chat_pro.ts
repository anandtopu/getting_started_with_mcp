/** Complete native Chat Pro backend for the shared browser UI. Loopback only. */
import { createServer, type IncomingMessage } from 'node:http';
import { once } from 'node:events';
import { randomBytes, timingSafeEqual } from 'node:crypto';
import { readFileSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { z } from 'zod';
import type { Tool, ElicitRequestParams, ElicitResult, CallToolResult } from '@modelcontextprotocol/client';
import { Ajv2020 } from 'ajv/dist/2020.js';
import { ChatConnection, hostConfig, type ServiceConfig } from './chat_services.ts';
import { type Model, type Proposal, fingerprint } from './advanced_host.ts';
import { modelTool, validateProposal } from './schemas.ts';
import { createModel, modelSettings } from './llm.ts';
import { root } from './data.ts';

const nonce = () => randomBytes(24).toString('base64url');
const messageSchema = z.object({ prompt: z.string().min(1).max(3000), provider: z.enum(['fake', 'openai', 'anthropic', 'gemini', 'ollama']).default('fake'), model: z.string().max(100).default('') }).strict();
const answerSchema = z.object({ id: z.string().min(1).max(100), action: z.enum(['accept', 'decline', 'cancel']), content: z.record(z.string(), z.unknown()).default({}) }).strict();
const scalarForm = z.object({ type: z.literal('object'), properties: z.record(z.string(), z.object({ type: z.enum(['boolean', 'string', 'number', 'integer']) }).passthrough()) }).passthrough();
export function fixtureModel(prompt: string): Model {
  const text = prompt.toLowerCase();
  const calls: Proposal[] = text.includes('deployed') ? [{ name: 'gateway__issues__read_issue', arguments: { issue_id: 1 } }]
    : text.includes('report') ? [{ name: 'gateway__quarterly_report', arguments: { ask_details: true } }]
    : text.includes('dashboard') ? [{ name: 'gateway__analytics_dashboard', arguments: {} }]
    : text.includes('close') ? [{ name: 'issues__bulk_close', arguments: { issue_ids: [1, 2] } }]
    : text.includes('note') ? [{ name: 'notes__create_note', arguments: { title: 'Release follow-up', body: 'Review the synthetic release checklist.' } }]
    : [{ name: 'gateway__workflow__triage_week', arguments: { week_start: '2026-07-13' } }, { name: 'gateway__workflow__draft_status', arguments: { week_start: '2026-07-13' } }];
  let index = 0;
  return async (_history, tools) => {
    if (index >= calls.length) return { text: 'Workflow complete. Review the tool evidence below; no model service was contacted.' };
    const call = { ...calls[index++], id: `practice-${index}` };
    if (!tools.some(tool => tool.name === call.name)) {
      const matches = tools.filter(tool => tool.name.endsWith('__' + call.name));
      if (matches.length === 1) call.name = matches[0].name;
    }
    return { calls: [call] };
  };
}

export class ChatSession {
  readonly csrf = nonce(); readonly expires = Date.now() + 1800000;
  readonly connections = new Map<string, ChatConnection>();
  events: Record<string, unknown>[] = []; status = 'ready';
  pending?: Record<string, unknown>;
  private decision?: { resolve: (answer: ElicitResult) => void; reject: (error: Error) => void };
  private controller?: AbortController;
  run?: Promise<void>; reconnecting = false;
  app?: { id: string; title: string; result: CallToolResult };
  appHtml = ''; private appBinding?: { connection: ChatConnection; tool: Tool };
  constructor(readonly config: ServiceConfig[], readonly id = nonce(), readonly taskPath = ':memory:') {}
  operationSignal() { return this.controller?.signal ?? AbortSignal.abort(); }
  emit = (type: string, value: Record<string, unknown>) => { this.events.push({ ...value, type }); this.events = this.events.slice(-120); };
  async start() {
    try {
      for (const config of this.config) { const connection = new ChatConnection(config, p => this.ask(p), this.emit, this.id, this.taskPath); this.connections.set(config.alias, connection); await connection.start(); }
    } catch (error) { await this.close(); throw error; }
  }
  snapshot() { return { status: this.status, events: this.events, pending: this.pending ?? null, connections: [...this.connections.values()].map(c => c.info), app: this.app ?? null }; }
  async question(kind: string, details: Record<string, unknown>): Promise<ElicitResult> {
    const signal = this.controller?.signal; signal?.throwIfAborted();
    if (this.decision) throw new Error('Another decision is pending');
    this.pending = { ...details, id: nonce(), kind }; this.status = 'waiting';
    let timer: ReturnType<typeof setTimeout> | undefined;
    const abort = () => this.decision?.reject(new Error('Operation cancelled'));
    try {
      return await new Promise<ElicitResult>((resolve, reject) => {
        this.decision = { resolve, reject }; timer = setTimeout(() => reject(new Error('Decision expired')), 120000); signal?.addEventListener('abort', abort, { once: true });
      });
    } finally { clearTimeout(timer); signal?.removeEventListener('abort', abort); this.pending = undefined; this.decision = undefined; this.status = 'running'; }
  }
  async ask(params: ElicitRequestParams): Promise<ElicitResult> {
    if (params.mode === 'url') { this.emit('error', { message: 'URL input requires a separately configured trusted flow.' }); return { action: 'decline' }; }
    const schema = scalarForm.parse(params.requestedSchema);
    if (Object.keys(schema.properties).length > 8 || JSON.stringify(schema).length > 8000) throw new Error('Unsupported input form');
    return this.question('input', { message: params.message, schema });
  }
  answer(value: unknown) {
    const answer = answerSchema.parse(value);
    if (!this.pending || this.pending.id !== answer.id || !this.decision) throw new Error('Decision expired or already answered');
    if (this.pending.kind === 'input' && answer.action === 'accept' && !new Ajv2020({ strict: false, validateFormats: false }).validate(this.pending.schema as object, answer.content)) throw new Error('Invalid input');
    const decision = this.decision; this.decision = undefined; decision.resolve(answer as ElicitResult);
  }
  private async catalog() {
    const tools: Tool[] = [];
    for (const [alias, connection] of this.connections) for (const tool of await connection.catalog()) {
      const name = `${alias}__${tool.name}`; if (!/^[a-zA-Z0-9_-]{1,64}$/.test(name)) throw new Error('Invalid tool name'); tools.push({ ...tool, name });
    }
    return tools;
  }
  private async execute(call: Proposal, signal: AbortSignal): Promise<CallToolResult> {
    signal.throwIfAborted();
    const proposed = structuredClone(call); const tool = (await this.catalog()).find(t => t.name === proposed.name);
    if (!tool) throw new Error('Unknown tool'); validateProposal(tool, proposed.arguments);
    const definition = fingerprint(tool); const [alias, ...parts] = proposed.name.split('__');
    const answer = await this.question('approval', { tool: proposed.name, description: tool.description, arguments: proposed.arguments, server: alias, schema: modelTool(tool).inputSchema, definition_hash: definition });
    signal.throwIfAborted();
    if (answer.action !== 'accept') { this.emit('declined', { tool: proposed.name }); return { content: [{ type: 'text', text: 'Call declined by user.' }], isError: true }; }
    const current = (await this.catalog()).find(t => t.name === proposed.name);
    if (!current || fingerprint(current) !== definition) throw new Error('Tool changed; review again');
    const localTool = { ...tool, name: parts.join('__') }; const connection = this.connections.get(alias)!;
    const args = { ...proposed.arguments }; if ('confirmed' in (tool.inputSchema.properties ?? {})) args.confirmed = true;
    const result = await connection.checkedCall(localTool, args, signal); signal.throwIfAborted();
    if (JSON.stringify(result).length > 16000) throw new Error('Tool result too large; request less data');
    this.emit('tool_result', { tool: proposed.name, result });
    if (localTool.name === 'analytics_dashboard' && !result.isError) {
      this.appHtml = await connection.readApp(); this.app = { id: nonce(), title: 'Lumen analytics', result }; this.appBinding = { connection, tool: localTool };
    }
    return result;
  }
  chat(prompt: string, model: Model) {
    if (this.run || this.reconnecting) throw new Error('Finish or cancel the current operation');
    this.controller = new AbortController(); const signal = this.controller.signal;
    this.status = 'running'; this.emit('user', { text: prompt });
    const timer = setTimeout(() => this.controller?.abort(), 240000);
    this.run = (async () => {
      try {
        const history: unknown[] = [{ role: 'user', content: prompt }]; const ids = new Set<string>(); let count = 0;
        for (let turn = 0; turn < 6; turn++) {
          signal.throwIfAborted(); const reply = await model(history, (await this.catalog()).map(modelTool)); signal.throwIfAborted();
          if (!reply.calls?.length) { this.emit('assistant', { text: reply.text ?? '' }); this.status = 'complete'; return; }
          history.push(reply);
          for (const call of reply.calls) {
            if (++count > 8) throw new Error('Tool budget exceeded'); const id = call.id ?? `fixture-${count}`;
            if (!id || ids.has(id)) throw new Error('Repeated call ID'); ids.add(id);
            history.push({ role: 'tool', id, name: call.name, result: await this.execute(call, signal) });
          }
        }
        throw new Error('Model turn budget exceeded');
      } catch {
        this.status = signal.aborted ? 'cancelled' : 'error';
        this.emit(this.status, { message: signal.aborted ? 'Operation stopped. Confirm any uncertain remote outcome before retrying.' : 'The workflow could not finish. Check configuration and connection status.' });
      } finally { clearTimeout(timer); this.pending = undefined; this.run = undefined; }
    })();
  }
  async cancel() { this.controller?.abort(); await this.run; }
  async refreshApp(value: unknown) {
    z.object({ name: z.literal('analytics_dashboard'), arguments: z.object({}).strict() }).strict().parse(value);
    if (!this.app || !this.appBinding) throw new Error('No displayed App');
    return this.appBinding.connection.checkedCall(this.appBinding.tool, {}, AbortSignal.timeout(10000));
  }
  async reconnect() {
    if (this.run || this.reconnecting) throw new Error('Finish or cancel the operation first');
    this.reconnecting = true; this.app = undefined; this.appBinding = undefined; this.appHtml = '';
    try { for (const connection of this.connections.values()) { await connection.close(); await connection.start(); } this.emit('info', { message: 'Reconnected. Ephemeral server data may have reset.' }); }
    finally { this.reconnecting = false; }
  }
  async close() { await this.cancel(); for (const c of this.connections.values()) await c.close(); this.connections.clear(); this.app = undefined; this.appBinding = undefined; }
}

class HttpError extends Error { constructor(readonly status: number, message: string) { super(message); } }
async function body(req: IncomingMessage) {
  let size = 0; const chunks: Buffer[] = [];
  for await (const chunk of req) { size += chunk.length; if (size > 64000) throw new HttpError(413, 'Request too large'); chunks.push(chunk); }
  try { return JSON.parse(Buffer.concat(chunks).toString() || '{}'); } catch { throw new HttpError(400, 'Invalid JSON'); }
}
export async function chatPro(port = 8768, config = hostConfig(), taskPath?: string) {
  if (!taskPath) { mkdirSync(resolve(root, '.runtime/typescript'), { recursive: true }); taskPath = resolve(root, '.runtime/typescript/tasks.db'); }
  const sessions = new Map<string, ChatSession>();
  const expire = async () => { for (const [id, session] of sessions) if (session.expires <= Date.now()) { sessions.delete(id); await session.close(); } };
  const janitor = setInterval(() => { void expire(); }, 15000); janitor.unref();
  const server = createServer(async (req, res) => {
    res.setHeader('Cache-Control', 'no-store'); res.setHeader('X-Content-Type-Options', 'nosniff'); res.setHeader('Referrer-Policy', 'no-referrer');
    res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; frame-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'");
    const json = (value: unknown, status = 200) => { res.writeHead(status, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(value)); };
    try {
      const address = server.address(); const actualPort = typeof address === 'object' && address ? address.port : port; const origin = `http://127.0.0.1:${actualPort}`;
      if (req.headers.host !== `127.0.0.1:${actualPort}`) throw new HttpError(421, 'Invalid Host');
      if ((req.headers.origin && req.headers.origin !== origin) || req.headers['sec-fetch-site'] === 'cross-site') throw new HttpError(403, 'Invalid Origin');
      const path = req.url ?? '/';
      const staticFiles: Record<string, [string, string]> = { '/': ['index.html', 'text/html'], '/assets/app.js': ['app.js', 'text/javascript'], '/assets/style.css': ['style.css', 'text/css'] };
      if (req.method === 'GET' && staticFiles[path]) { const [file, type] = staticFiles[path]; res.writeHead(200, { 'Content-Type': type }); res.end(readFileSync(resolve(root, 'common/web_ui', file))); return; }
      if (!['GET', 'POST'].includes(req.method ?? '')) throw new HttpError(405, 'Method not allowed');
      const id = /(?:^|;\s*)lumen_session=([A-Za-z0-9_-]+)/.exec(req.headers.cookie ?? '')?.[1] ?? '';
      let session = sessions.get(id);
      if (path === '/api/session' && req.method === 'POST') {
        if (req.headers['x-lumen-client'] !== 'web') throw new HttpError(403, 'Use the local web interface');
        z.object({}).strict().parse(await body(req)); await expire();
        if (!session || session.expires <= Date.now()) {
          if (sessions.size >= 4) throw new HttpError(429, 'Session capacity reached');
          session = new ChatSession(config, nonce(), taskPath); sessions.set(session.id, session);
          try { await session.start(); } catch (error) { sessions.delete(session.id); throw error; }
        }
        res.setHeader('Set-Cookie', `lumen_session=${session.id}; HttpOnly; SameSite=Strict; Path=/; Max-Age=1800`); json({ csrf: session.csrf, ...session.snapshot() }); return;
      }
      if (!session || session.expires <= Date.now()) throw new HttpError(401, 'Session expired. Reload to reconnect.');
      if (req.method === 'GET' && path === '/api/state') { json(session.snapshot()); return; }
      if (req.method === 'GET' && path === `/api/app-view/${session.app?.id}` && session.app) {
        res.setHeader('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; frame-src 'none'; form-action 'none'; base-uri 'none'; sandbox allow-scripts");
        res.writeHead(200, { 'Content-Type': 'text/html' }); res.end(session.appHtml); return;
      }
      if (req.method !== 'POST') throw new HttpError(404, 'Not found');
      const actual = Buffer.from(String(req.headers['x-csrf-token'] ?? '')); const expected = Buffer.from(session.csrf);
      if (actual.length !== expected.length || !timingSafeEqual(actual, expected)) throw new HttpError(403, 'Request verification failed');
      const input = await body(req);
      if (path === '/api/chat') {
        if (session.run || session.reconnecting) throw new HttpError(409, 'Finish or cancel the current operation');
        const message = messageSchema.parse(input); let model: Model;
        if (message.provider === 'fake') model = fixtureModel(message.prompt);
        else {
          const settings = modelSettings({ ...process.env, LLM_PROVIDER: message.provider, LLM_MODEL: message.model || process.env[message.provider.toUpperCase() + '_MODEL'] || (process.env.LLM_PROVIDER === message.provider ? process.env.LLM_MODEL : '') });
          // Associate provider fetch with this workflow; cancellation also stops HTTP.
          model = createModel(settings, (url, init) => fetch(url, { ...init, signal: AbortSignal.any([init?.signal ?? AbortSignal.timeout(60000), session!.operationSignal()]) }));
        }
        session.chat(message.prompt, model); json({ accepted: true }, 202);
      } else if (path === '/api/answer') { session.answer(input); json({ accepted: true }); }
      else if (path === '/api/app-call') { json(await session.refreshApp(input)); }
      else {
        z.object({}).strict().parse(input);
        if (path === '/api/cancel') { await session.cancel(); json({ cancelled: true }); }
        else if (path === '/api/reconnect') { if (session.run || session.reconnecting) throw new HttpError(409, 'Finish or cancel the current operation'); await session.reconnect(); json({ connected: true }); }
        else if (path === '/api/close') { sessions.delete(session.id); await session.close(); res.setHeader('Set-Cookie', 'lumen_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0'); json({ closed: true }); }
        else throw new HttpError(404, 'Not found');
      }
    } catch (error) { json({ detail: error instanceof HttpError ? error.message : 'Request could not be completed. Check the input and server configuration.' }, error instanceof HttpError ? error.status : 400); }
  });
  server.requestTimeout = 15000; server.headersTimeout = 10000;
  const close = async () => { clearInterval(janitor); server.closeAllConnections(); await new Promise<void>(resolve => server.close(() => resolve())); await Promise.allSettled([...sessions.values()].map(s => s.close())); sessions.clear(); };
  try { server.listen(port, '127.0.0.1'); await once(server, 'listening'); } catch (error) { await close(); throw error; }
  return { server, sessions, close };
}
