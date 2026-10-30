/** Compare 25 endpoint-shaped tools with six workflow tools on identical data. */
import { DatabaseSync, type SQLOutputValue } from 'node:sqlite';
import { resolve } from 'node:path';
import { McpServer } from '@modelcontextprotocol/server';
import { z } from 'zod';
import { root } from './data.ts';
import { read, structured, failure } from './notes.ts';
import { inMemory } from './clients.ts';

const tables=['issues','projects','users','comments','labels'] as const;
type Table=typeof tables[number];
type Row=Record<string,SQLOutputValue>;
const limit=z.number().int().min(1).max(20).default(10);
function rows(table:Table):Row[] {
  const db=new DatabaseSync(resolve(root,'data/issues.db'),{readOnly:true});
  try {return db.prepare(`SELECT * FROM ${table} ORDER BY id`).all();}
  finally {db.close();}
}
function page(values:Row[],after:number,count:number) {
  const eligible=values.filter(row=>Number(row.id)>after);const items=eligible.slice(0,count);
  return {items,next_after:eligible.length>count?Number(items.at(-1)!.id):null};
}
function brief(id:number,detailed=false) {
  const issue=rows('issues').find(row=>row.id===id);
  if(!issue)return undefined;
  return detailed?{...issue,comments:rows('comments').filter(row=>row.issue_id===id).map(row=>row.body)}:
    {id:issue.id,title:issue.title,status:issue.status,priority:issue.priority};
}
function triage(start:string) {
  const stop=new Date(start+'T00:00:00Z');stop.setUTCDate(stop.getUTCDate()+7);
  const items=rows('issues').filter(row=>String(row.created_at)>=start && String(row.created_at)<stop.toISOString().slice(0,10));
  const active=items.filter(row=>row.status!=='closed');
  return {week_start:start,total:items.length,active:active.length,high_priority_ids:active.filter(row=>row.priority==='high').map(row=>row.id)};
}

export function mirrorServer() {
  const server=new McpServer({name:'Lumen TypeScript endpoint mirror',version:'1'});
  for(const table of tables) {
    server.registerTool(`list_${table}`,{description:`List ${table} records.`,inputSchema:z.object({after:z.number().int().min(0).default(0),limit}),annotations:read},args=>structured(page(rows(table),args.after,args.limit)));
    server.registerTool(`get_${table}`,{description:`Get ${table} record.`,inputSchema:z.object({row_id:z.number().int()}),annotations:read},args=>{
      const row=rows(table).find(row=>row.id===args.row_id);return row?structured(row):failure('Record not found. List records and choose an existing ID.');
    });
    server.registerTool(`count_${table}`,{description:`Count ${table} records.`,inputSchema:z.object({}),annotations:read},()=>structured({count:rows(table).length}));
    server.registerTool(`fields_${table}`,{description:`Describe ${table} fields.`,inputSchema:z.object({}),annotations:read},()=>structured({fields:Object.keys(rows(table)[0])}));
    server.registerTool(`find_${table}`,{description:`Find text in ${table} records.`,inputSchema:z.object({text:z.string().max(100),limit}),annotations:read},args=>structured(page(rows(table).filter(row=>JSON.stringify(row).toLowerCase().includes(args.text.toLowerCase())),0,args.limit)));
  }
  return server;
}

export function taskToolsServer() {
  const server=new McpServer({name:'Lumen TypeScript task tools',version:'1'});
  const mode=z.enum(['concise','detailed']).default('concise');
  const week=z.object({week_start:z.iso.date().default('2026-07-13')});
  server.registerTool('search_issues',{description:'Find items by title. Follow next_after; start concise, then fetch details.',inputSchema:z.object({query:z.string().max(100).default(''),after:z.number().int().min(0).default(0),limit,mode}),annotations:read},args=>{
    const result=page(rows('issues').filter(row=>String(row.title).toLowerCase().includes(args.query.toLowerCase())),args.after,args.limit);
    return structured({...result,items:result.items.map(row=>brief(Number(row.id),args.mode==='detailed'))});
  });
  server.registerTool('issue_brief',{description:'Read a known issue ID. Choose detailed for comments and ownership.',inputSchema:z.object({issue_id:z.number().int(),mode}),annotations:read},args=>{
    const value=brief(args.issue_id,args.mode==='detailed');return value?structured(value):failure('Issue not found. Use search_issues and choose an ID from its results.');
  });
  server.registerTool('triage_week',{description:'Summarize seven days of synthetic work items from an ISO start date.',inputSchema:week,annotations:read},args=>structured(triage(args.week_start)));
  server.registerTool('draft_status',{description:'Draft a weekly status update from evidence. Returns text; never publishes.',inputSchema:week,annotations:read},args=>{
    const evidence=triage(args.week_start);return structured({draft:`Week ${args.week_start}: ${evidence.total} work items; ${evidence.active} active.`,published:false,evidence});
  });
  server.registerTool('project_summary',{description:'Count a project work inventory without paging through all issues.',inputSchema:z.object({project_id:z.number().int().min(1).max(5)}),annotations:read},args=>{
    const items=rows('issues').filter(row=>row.project_id===args.project_id);return structured({...args,total:items.length,active:items.filter(row=>row.status!=='closed').length});
  });
  server.registerTool('team_load',{description:'Count active work assigned to one synthetic employee.',inputSchema:z.object({assignee_id:z.number().int().min(1).max(80)}),annotations:read},args=>structured({...args,active:rows('issues').filter(row=>row.assignee_id===args.assignee_id && row.status!=='closed').length}));
  return server;
}

export async function designEvaluation() {
  const output:Record<string,unknown>={mode:'deterministic retrieval; not live model accuracy'};
  for(const [label,factory,name,key] of [
    ['mirror',mirrorServer,'get_issues','row_id'],['task_tools',taskToolsServer,'issue_brief','issue_id'],
  ] as const) {
    await inMemory(factory,async client=>{
      const catalog=(await client.listTools()).tools;let completed=0;
      for(const id of [1,13,55,112,239,400]) {
        const response=await client.callTool({name,arguments:{[key]:id}});
        const actual=response.structuredContent as {id?:number;status?:string};
        const expected=brief(id)!;
        if(!response.isError && actual.id===expected.id && actual.status===expected.status)completed++;
      }
      output[label]={tools:catalog.length,completed,cases:6,catalog_characters:JSON.stringify(catalog).length};
    });
  }
  return output;
}
