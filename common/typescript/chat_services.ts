/** Fixed native service profiles and explicitly configured remote MCP connections. */
import { Client, InMemoryTransport, StreamableHTTPClientTransport, type CallToolResult, type Tool, type ElicitRequestParams, type ElicitResult } from '@modelcontextprotocol/client';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { McpServer } from '@modelcontextprotocol/server';
import { readFileSync } from 'node:fs';
import { z } from 'zod';
import { notesServer } from './notes.ts';
import { remoteWorkspace } from './remote.ts';
import { workflowServer } from './workflow.ts';
import { nativeWorkspace, addDashboard, appUri } from './workspace.ts';
import { Tasks, tasksID } from './task_receiver.ts';
import { RpcPeer, serveRaw } from './protocol_peer.ts';
import { fingerprint } from './advanced_host.ts';
import { publicEndpoint } from './advanced_policy.ts';

const serverConfig = z.object({ alias: z.string().regex(/^[a-z][a-z0-9_]{0,15}$/), profile: z.enum(['notes', 'issues', 'gateway', 'workflow']).default('notes'), mode: z.enum(['current', 'auto', 'legacy']).default('current'), url: z.string().optional(), token_env: z.string().regex(/^[A-Z][A-Z0-9_]{0,79}$/).optional() }).strict();
export type ServiceConfig = z.infer<typeof serverConfig>;
export type Ask = (params: ElicitRequestParams) => Promise<ElicitResult>;
export type Emit = (kind: string, value: Record<string, unknown>) => void;
export function hostConfig(path?: string): ServiceConfig[] {
  if (!path) return ['notes', 'issues', 'gateway'].map(profile => serverConfig.parse({ alias: profile, profile }));
  const file = readFileSync(path); if (file.length > 16000) throw new Error('Host configuration exceeds 16 KB');
  const config = z.object({ servers: z.array(serverConfig).min(1).max(5) }).strict().parse(JSON.parse(file.toString()));
  if (new Set(config.servers.map(s => s.alias)).size !== config.servers.length) throw new Error('Duplicate alias');
  for (const s of config.servers) {
    if (s.url && new URL(publicEndpoint(s.url)).pathname !== '/mcp') throw new Error('Use a configured /mcp resource');
    if (s.token_env && !s.url) throw new Error('Tokens are only for remote resources');
  }
  return config.servers;
}

export class ChatConnection {
  client?: Client;
  private closers: (() => Promise<unknown> | void)[] = [];
  private tasks?: RpcPeer;
  private appClient?: Client;
  constructor(readonly config: ServiceConfig, readonly ask: Ask, readonly emit: Emit, readonly owner: string, readonly taskPath = ':memory:') {}
  get info() { return { alias: this.config.alias, protocol: this.client?.getProtocolEra() ?? 'disconnected' }; }
  async start() {
    try {
      const client = new Client({ name: 'Lumen Chat Pro TypeScript', version: '1' }, { versionNegotiation: { mode: this.config.mode === 'current' ? { pin: '2026-07-28' } : this.config.mode }, capabilities: { elicitation: { form: {} } } });
      this.client = client; this.closers.push(() => client.close());
      client.setRequestHandler('elicitation/create', request => this.ask(request.params));
      if (this.config.url) {
        const token = this.config.token_env ? process.env[this.config.token_env] : undefined;
        if (this.config.token_env && !token) throw new Error('Configured server token is missing');
        await client.connect(new StreamableHTTPClientTransport(new URL(this.config.url), { requestInit: token ? { headers: { Authorization: `Bearer ${token}` } } : undefined }), { timeout: 5000 });
      } else {
        let factory: () => McpServer;
        if (this.config.profile === 'issues') { const issues = remoteWorkspace(true); this.closers.unshift(issues.close); factory = issues.factory; }
        else if (this.config.profile === 'gateway') {
          const workspace = await nativeWorkspace(() => ({ subject: this.owner, scopes: ['workspace:read', 'workspace:write'] }));
          this.closers.unshift(workspace.close); factory = workspace.factory;
          // SDK 2.4 cannot decode custom resultType:task. Keep the Tasks wire
          // connection separate, with official framing and a bounded RPC peer.
          const receiver = new Tasks(this.taskPath, () => this.owner); this.closers.unshift(() => receiver.close());
          const [left, right] = InMemoryTransport.createLinkedPair();
          await serveRaw(left, (method, params, caps) => receiver.dispatch(method, params, caps));
          const peer = new RpcPeer(right, { extensions: { [tasksID]: {} }, elicitation: { form: {} } });
          this.tasks = peer; this.closers.push(() => left.close(), () => peer.close()); await peer.start(); await peer.request('server/discover');
          const app = new Client({ name: 'Lumen App host', version: '1' }, { versionNegotiation: { mode: { pin: '2026-07-28' } } });
          const [a, b] = InMemoryTransport.createLinkedPair();
          const handle = serveStdio(() => { const s = new McpServer({ name: 'Lumen analytics App', version: '1' }); addDashboard(s); return s; }, { transport: a });
          this.closers.push(() => handle.close(), () => app.close()); this.appClient = app; await app.connect(b);
        } else factory = this.config.profile === 'notes' ? notesServer : workflowServer;
        const [left, right] = InMemoryTransport.createLinkedPair();
        const handle = serveStdio(factory, { transport: left }); this.closers.push(() => handle.close());
        await client.connect(right, { timeout: 5000 });
      }
      if (client.getProtocolEra() === 'modern') await client.discover();
      await this.catalog();
      this.emit('connection', this.info); return this;
    } catch (error) { await this.close(); throw error; }
  }
  async catalog(): Promise<Tool[]> {
    if (!this.client) throw new Error('Service disconnected');
    const tools: Tool[] = []; const seen = new Set<string>(); let cursor: string | undefined;
    for (let page = 0; page < 20; page++) {
      const result = await this.client.listTools({ cursor }, { timeout: 5000, cacheMode: 'refresh' }); tools.push(...result.tools); cursor = result.nextCursor;
      if (!cursor) break;
      if (seen.has(cursor) || page === 19) throw new Error('Catalog page budget exceeded'); seen.add(cursor);
    }
    if (this.tasks) tools.push(...(await this.tasks.request('tools/list')).tools as Tool[]);
    if (this.appClient) tools.push(...(await this.appClient.listTools(undefined, { cacheMode: 'refresh' })).tools);
    if (tools.length > 200 || new Set(tools.map(t => t.name)).size !== tools.length) throw new Error('Invalid catalog');
    return tools;
  }
  async checkedCall(reviewed: Tool, args: Record<string, unknown>, signal: AbortSignal): Promise<CallToolResult> {
    for (let attempt = 0; attempt < 2; attempt++) {
      signal.throwIfAborted();
      const current = (await this.catalog()).find(t => t.name === reviewed.name);
      if (!current || fingerprint(current) !== fingerprint(reviewed)) throw new Error('Tool changed; review again');
      signal.throwIfAborted();
      try {
        if (reviewed.name === 'quarterly_report' && this.tasks) return await this.report(args, signal);
        const client = reviewed.name === 'analytics_dashboard' && this.appClient ? this.appClient : this.client!;
        return await client.callTool({ name: reviewed.name, arguments: args }, { timeout: 180000, signal, onprogress: p => this.emit('progress', { ...p }) }) as CallToolResult;
      } catch (error) {
        if (signal.aborted || attempt || !['search_notes', 'read_issue', 'workflow__triage_week', 'workflow__draft_status'].includes(reviewed.name) || !(error instanceof Error) || !/closed|timeout|connect/i.test(error.message)) throw error;
        await this.close(); await this.start();
      }
    }
    throw new Error('Reconnect budget exceeded');
  }
  private async report(args: Record<string, unknown>, signal: AbortSignal): Promise<CallToolResult> {
    const peer = this.tasks!;
    let task = await peer.request('tools/call', { name: 'quarterly_report', arguments: args }); const taskId = String(task.taskId);
    try {
      for (let poll = 0; poll < 40; poll++) {
        signal.throwIfAborted(); this.emit('task', task);
        if (task.status === 'completed') return task.result as CallToolResult;
        if (['failed', 'cancelled'].includes(String(task.status))) return { content: [{ type: 'text', text: 'Report cancelled.' }], isError: true };
        if (task.status === 'input_required') {
          const requests = z.record(z.string(), z.object({ method: z.literal('elicitation/create'), params: z.record(z.string(), z.unknown()) })).parse(task.inputRequests);
          if (Object.keys(requests).length > 8) throw new Error('Too many Task inputs');
          const inputResponses: Record<string, unknown> = {};
          for (const [id, request] of Object.entries(requests)) inputResponses[id] = await this.ask(request.params as ElicitRequestParams);
          signal.throwIfAborted(); await peer.request('tasks/update', { taskId, inputResponses });
        }
        task = await peer.request('tasks/get', { taskId });
      }
      throw new Error('Task poll budget exceeded');
    } finally {
      if (task.status !== 'completed' && task.status !== 'cancelled') { await peer.request('tasks/cancel', { taskId }); this.emit('task', { taskId, status: 'cancelled' }); }
    }
  }
  async readApp() {
    if (!this.appClient) throw new Error('App is not available on this connection');
    const resource = await this.appClient.readResource({ uri: appUri }, { timeout: 5000 });
    const content = resource.contents[0]; if (!content || !('text' in content) || content.text.length > 1500000) throw new Error('Invalid App resource');
    return content.text;
  }
  async close() {
    this.client = undefined; this.tasks = undefined; this.appClient = undefined;
    for (const close of this.closers.splice(0).reverse()) { try { await close(); } catch { /* Continue releasing all owned resources. */ } }
  }
}
