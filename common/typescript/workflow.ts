/** Read-only triage and draft tools shared by three native framework runtimes. */
import { McpServer } from '@modelcontextprotocol/server';
import { DatabaseSync } from 'node:sqlite';
import { resolve } from 'node:path';
import { z } from 'zod';
import { root } from './data.ts';
import { read, structured } from './notes.ts';
export function workflowServer() {
  const server=new McpServer({name:'Lumen triage workflow',version:'1'});
  const schema=z.object({week_start:z.literal('2026-07-13')});
  function evidence() {
    const db=new DatabaseSync(resolve(root,'data/issues.db'),{readOnly:true});
    try {return db.prepare("SELECT id,title,status,priority FROM issues WHERE created_at>=? AND created_at<? ORDER BY id LIMIT 20").all('2026-07-13','2026-07-20');}
    finally {db.close();}
  }
  server.registerTool('triage_week',{description:'Read at most 20 issues created in the fixture week. No changes.',inputSchema:schema,annotations:read},()=>structured({issues:evidence()}));
  server.registerTool('draft_status',{description:'Draft a factual status summary of the same bounded week; never publish.',inputSchema:schema,annotations:read},()=>structured({draft:`Reviewed ${evidence().length} synthetic issues for 2026-07-13. No status changes were made.`}));
  return server;
}
