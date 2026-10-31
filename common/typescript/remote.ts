/** Shared application state survives the SDK's per-request server factory. */
import { DatabaseSync } from 'node:sqlite';
import { resolve } from 'node:path';
import { setTimeout as pause } from 'node:timers/promises';
import { McpServer, ResourceTemplate, completable, InMemoryServerEventBus, inputRequired, acceptedContent } from '@modelcontextprotocol/server';
import { ReviewLedger } from './advanced_policy.ts';
import { z } from 'zod';
import { root } from './data.ts';
import { wikiText } from './wiki.ts';
import { structured, failure, read as readAnnotation, write, replace } from './notes.ts';
import { serveHttp } from './http.ts';

export function remoteWorkspace(withForms = false) {
  const bus = new InMemoryServerEventBus();
  const source = new DatabaseSync(resolve(root, 'data/issues.db'), { readOnly: true });
  const db = new DatabaseSync(':memory:');
  db.exec('CREATE TABLE issues(id INTEGER PRIMARY KEY, project_id INTEGER, title TEXT, status TEXT, priority TEXT, assignee_id INTEGER, created_at TEXT); CREATE TABLE receipts(key TEXT PRIMARY KEY, issue_id INTEGER, binding TEXT)');
  const insert = db.prepare('INSERT INTO issues VALUES(?,?,?,?,?,?,?)');
  for (const row of source.prepare('SELECT * FROM issues').all()) {
    insert.run(row.id, row.project_id, row.title, row.status, row.priority, row.assignee_id, row.created_at);
  }
  source.close();
  let nextId = Number(db.prepare('SELECT max(id) AS id FROM issues').get()!.id) + 1;
  let active = 0;
  let review = 'No review yet';
  const decisions = new ReviewLedger();
  const issue = z.object({ title: z.string().min(1).max(120), project_id: z.number().int().min(1).max(5).default(1), priority: z.enum(['low', 'medium', 'high']).default('medium') }).strict();
  const read = (id: number) => db.prepare('SELECT * FROM issues WHERE id=?').get(id);
  function factory() {
    const server = new McpServer({ name: 'Lumen remote workspace', version: '4.0' },
      { capabilities: { resources: { subscribe: true } } });
    const approval = z.object({ approve: z.boolean().meta({ title: 'Approve' }) });
    if (withForms) server.registerTool('bulk_close', { description: 'Close up to ten synthetic issues after a separate form decision.', annotations: replace,
      inputSchema: z.object({ issue_ids: z.array(z.number().int().positive()).min(1).max(10), confirmed: z.boolean().default(false) }) }, ({ issue_ids, confirmed }, ctx) => {
      if (!confirmed || issue_ids.some(id => !read(id))) return failure('Confirm existing issue IDs first.');
      const binding = JSON.stringify(issue_ids);
      const state = ctx.mcpReq.requestState<string>();
      if (!state) return inputRequired({ requestState: decisions.issue(binding), inputRequests: { decision: inputRequired.elicit({ message: `Close these synthetic issues: ${issue_ids.join(', ')}?`, requestedSchema: approval }) } });
      decisions.take(state, binding);
      if (acceptedContent(ctx.mcpReq.inputResponses, 'decision', approval)?.approve !== true) return structured({ closed: [] });
      db.exec('BEGIN');
      try { for (const id of issue_ids) db.prepare("UPDATE issues SET status='closed' WHERE id=?").run(id); db.exec('COMMIT'); }
      catch (error) { db.exec('ROLLBACK'); throw error; }
      return structured({ closed: issue_ids });
    });
    server.registerTool('read_issue', { annotations:readAnnotation, inputSchema: z.object({ issue_id: z.number().int() }) }, ({ issue_id }) => {
      const row = read(issue_id); return row ? structured(row) : failure('Issue not found');
    });
    server.registerTool('create_issue', { annotations:write, inputSchema: z.object({ issue, operation_key: z.string().min(1).max(80), confirmed: z.boolean().default(false) }) }, args => {
      if (!args.confirmed) return failure('Confirm this exact write in the host first.');
      const binding = JSON.stringify(args.issue);
      const prior = db.prepare('SELECT * FROM receipts WHERE key=?').get(args.operation_key);
      if (prior) {
        if (prior.binding !== binding) return failure('Operation key belongs to different arguments');
        const existing = read(Number(prior.issue_id));
        return existing ? structured(existing) : failure('This operation created an issue that was deleted');
      }
      db.exec('BEGIN');
      try {
        const result = db.prepare("INSERT INTO issues(id,project_id,title,status,priority,created_at) VALUES(?,?,?,'open',?,'2026-10-30')").run(nextId++, args.issue.project_id, args.issue.title, args.issue.priority);
        db.prepare('INSERT INTO receipts VALUES(?,?,?)').run(args.operation_key, result.lastInsertRowid, binding);
        db.exec('COMMIT'); return structured(read(Number(result.lastInsertRowid))!);
      } catch (error) { db.exec('ROLLBACK'); throw error; }
    });
    server.registerTool('update_issue', { annotations:replace, inputSchema: z.object({ issue_id: z.number().int(), status: z.enum(['open', 'in_progress', 'closed']), confirmed: z.boolean().default(false) }) }, args => {
      if (!args.confirmed || !read(args.issue_id)) return failure('Confirm an existing issue');
      db.prepare('UPDATE issues SET status=? WHERE id=?').run(args.status, args.issue_id);
      return structured(read(args.issue_id)!);
    });
    server.registerTool('delete_issue', { annotations:replace, inputSchema: z.object({ issue_id: z.number().int(), confirmed: z.boolean().default(false) }) }, args => {
      if (!args.confirmed || !read(args.issue_id)) return failure('Confirm an existing issue');
      db.exec('BEGIN');
      try {
        db.prepare('DELETE FROM issues WHERE id=?').run(args.issue_id);
        db.exec('COMMIT');
      } catch (error) { db.exec('ROLLBACK'); throw error; }
      return structured({ deleted: args.issue_id });
    });
    server.registerTool('route_region', { annotations:readAnnotation, inputSchema: z.object({ region: z.string().meta({ 'x-mcp-header': 'Region' }) }) }, args => structured(args));
    server.registerTool('report_status', { annotations:readAnnotation, inputSchema: z.object({}) }, () => structured({ active, issue_count: db.prepare('SELECT count(*) AS n FROM issues').get()!.n }));
    server.registerTool('quarterly_report', { annotations:readAnnotation, inputSchema: z.object({ quarter: z.enum(['Q1', 'Q2', 'Q3', 'Q4']).default('Q1'), delay: z.number().min(0).max(1).default(0.02) }) }, async ({ quarter, delay }, ctx) => {
      active++;
      try {
        for (let i = 1; i <= 4; i++) {
          await pause(delay * 1000, undefined, { signal: ctx.mcpReq.signal });
          const progressToken = ctx.mcpReq._meta?.progressToken;
          if (progressToken !== undefined) await ctx.mcpReq.notify({ method: 'notifications/progress', params: { progressToken, progress: i, total: 4, message: `${quarter}: section ${i}` } });
        }
        return structured({ quarter, scope: 'all fixture issues (simulated report)', counts: db.prepare('SELECT status, count(*) AS count FROM issues GROUP BY status').all() });
      } finally { active--; }
    });
    server.registerPrompt('report_brief', { argsSchema: z.object({ quarter: completable(z.string(), value => ['Q1', 'Q2', 'Q3', 'Q4'].filter(q => q.startsWith(value))) }) }, ({ quarter }) => ({ messages: [{ role: 'user', content: { type: 'text', text: `Summarize ${quarter}; dates are simulated.` } }] }));
    server.registerResource('wiki', new ResourceTemplate('wiki://{space}/{page}', { list: undefined }), {}, (uri, args) => ({ contents: [{ uri: uri.href, text: wikiText(String(args.space), String(args.page)) }] }));
    server.registerTool('find_page', { annotations:readAnnotation, inputSchema: z.object({ space: z.string().default('engineering'), page: z.string().default('page-01') }) }, ({ space, page }) => {
      wikiText(space, page);
      return { content: [{ type: 'resource_link', name: page, uri: `wiki://${space}/${page}`, mimeType: 'text/markdown' }] };
    });
    server.registerResource('review', 'workspace://review', {}, uri => ({ contents: [{ uri: uri.href, text: review }] }));
    server.registerTool('publish_review', { annotations:replace, inputSchema: z.object({ text: z.string().max(500), confirmed:z.boolean().default(false) }) }, async ({ text, confirmed }) => {
      if (!confirmed) return failure('Confirm this exact write in the host first.');
      review = text; bus.publish({ kind: 'resource_updated', uri: 'workspace://review' }); return structured({ updated: true });
    });
    return server;
  }
  return { factory, bus, close: () => db.close() };
}

export function main() {
  const offset = process.argv.indexOf('--port');
  const port = offset < 0 ? 8000 : Number(process.argv[offset + 1]);
  const workspace = remoteWorkspace();
  const app = serveHttp(workspace.factory, port, workspace.bus);
  app.start();
  process.on('SIGTERM', async () => {
    await app.handler.close(); app.server.close(); workspace.close();
  });
}
