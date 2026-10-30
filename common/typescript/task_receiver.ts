/** Current Tasks extension over the SDK transport (2.4 has no task-result hook), backed by SQLite.
 * Single-process teaching receiver: polling resumes durable work after restart.
 */
import { DatabaseSync } from 'node:sqlite';
import { randomBytes } from 'node:crypto';
import { InMemoryTransport, type ClientCapabilities } from '@modelcontextprotocol/client';
import { RpcPeer, serveRaw } from './protocol_peer.ts';
import { z } from 'zod';
import { strict as assert } from 'node:assert';
import { read } from './notes.ts';

export const tasksID='io.modelcontextprotocol/tasks';
const params=z.object({taskId:z.string().min(1).max(100)});
export class Tasks {
  readonly db:DatabaseSync;
  constructor(path=':memory:',readonly principal=()=> 'local-learner') {
    this.db=new DatabaseSync(path);
    this.db.exec('CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, owner TEXT, expires REAL, body TEXT)');
  }
  load(id:string) {
    const row=this.db.prepare('SELECT * FROM tasks WHERE id=? AND owner=? AND expires>?').get(id,this.principal(),Date.now());
    if(!row) throw new Error('Unknown or expired task');
    return JSON.parse(String(row.body));
  }
  save(task:Record<string,unknown>) {
    task.lastUpdatedAt=new Date().toISOString();
    this.db.prepare('UPDATE tasks SET body=? WHERE id=?').run(JSON.stringify(task),String(task.taskId));
  }
  dispatch(method:string, data:Record<string,unknown>, caps:ClientCapabilities):Record<string,unknown> {
    if(method==='server/discover') return {supportedVersions:['2026-07-28'],capabilities:{tools:{},extensions:{[tasksID]:{}}},ttlMs:0,cacheScope:'private'};
    if(method==='tools/list') return {tools:[{name:'quarterly_report',description:'A durable synthetic report. Ask for detail input when supported.',inputSchema:{type:'object',properties:{ask_details:{type:'boolean'}}},annotations:read}],ttlMs:0,cacheScope:'private'};
    if(method==='tools/call') {
      const p=z.object({name:z.literal('quarterly_report'),arguments:z.object({ask_details:z.boolean().default(false)}).default({ask_details:false})}).parse(data);
      if(!caps.extensions?.[tasksID]) return {content:[{type:'text',text:'400 synthetic issues'}],structuredContent:{total:400}};
      if(p.arguments.ask_details && !caps.elicitation?.form) throw new Error('Form capability required');
      this.db.prepare('DELETE FROM tasks WHERE expires<=?').run(Date.now());
      if(Number(this.db.prepare('SELECT count(*) AS n FROM tasks').get()!.n)>=100) throw new Error('Task capacity reached');
      const stamp=new Date().toISOString();
      const task={taskId:randomBytes(24).toString('base64url'),status:p.arguments.ask_details?'input_required':'working',createdAt:stamp,lastUpdatedAt:stamp,ttlMs:300000,pollIntervalMs:25,...(p.arguments.ask_details?{inputRequests:{details:{method:'elicitation/create',params:{mode:'form',message:'Include detailed counts?',requestedSchema:{type:'object',properties:{include_details:{type:'boolean'}},required:['include_details']}}}}}:{})};
      this.db.prepare('INSERT INTO tasks VALUES(?,?,?,?)').run(task.taskId,this.principal(),Date.now()+300000,JSON.stringify(task));
      return {resultType:'task',...task};
    }
    if(!caps.extensions?.[tasksID]) throw new Error('Tasks capability required');
    const p=params.parse(data);const task=this.load(p.taskId);
    if(method==='tasks/get') {
      if(task.status==='working') {task.status='completed';task.result={resultType:'complete',content:[{type:'text',text:'400 synthetic issues'}],structuredContent:{total:400,detailed:task.detailed??false}};this.save(task);}
      return {resultType:'complete',...task};
    }
    if(method==='tasks/update') {
      const p=params.extend({inputResponses:z.record(z.string(),z.unknown())}).parse(data);
      if(task.status==='input_required' && p.inputResponses.details) {
        const answer=z.object({action:z.enum(['accept','decline','cancel']),content:z.object({include_details:z.boolean()}).optional()}).parse(p.inputResponses.details);
        if(answer.action==='accept' && !answer.content) throw new Error('Details answer required');
        task.status=answer.action==='accept'?'working':'cancelled';task.detailed=answer.content?.include_details===true;delete task.inputRequests;this.save(task);
      }
      return {resultType:'complete'};
    }
    if(method==='tasks/cancel') {if(['working','input_required'].includes(task.status)){task.status='cancelled';delete task.inputRequests;this.save(task);}return {};}
    throw new Error('Unknown method');
  }
  close(){this.db.close();}
}

export async function taskDemo() {
  const tasks=new Tasks();const [a,b]=InMemoryTransport.createLinkedPair();
  await serveRaw(a,(method,p,caps)=>tasks.dispatch(method,p,caps));
  const client=new RpcPeer(b,{extensions:{[tasksID]:{}},elicitation:{form:{}}});
  try {
    await client.start();await client.request('server/discover');
    const task=await client.request('tools/call',{name:'quarterly_report',arguments:{ask_details:true}});
    assert.equal(task.resultType,'task');const taskId=String(task.taskId);
    await client.request('tasks/update',{taskId,inputResponses:{details:{action:'accept',content:{include_details:true}}}});
    const done=await client.request('tasks/get',{taskId});assert.equal(done.status,'completed');return done;
  } finally {await client.close();await a.close();tasks.close();}
}
