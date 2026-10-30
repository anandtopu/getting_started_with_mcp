import { describe, expect, it } from 'vitest';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { once } from 'node:events';
import { Tasks, tasksID } from './task_receiver.ts';
import { inMemory } from './clients.ts';
import { notesServer } from './notes.ts';
import { CourseHost } from './advanced_host.ts';
import { webHost } from './web_host.ts';

describe('Phase 8 authorization boundaries', () => {
  it('persists task ownership and treats declined input as cancellation', () => {
    const folder = mkdtempSync(join(tmpdir(), 'lumen-task-'));
    const path = join(folder, 'tasks.db');
    let principal = 'reader-a';
    const caps = { extensions: { [tasksID]: {} }, elicitation: { form: {} } };
    let tasks = new Tasks(path, () => principal);
    try {
      const task = tasks.dispatch('tools/call', {name:'quarterly_report',arguments:{ask_details:true}}, caps);
      tasks.close(); tasks = new Tasks(path, () => principal);
      principal = 'reader-b';
      expect(() => tasks.dispatch('tasks/get', {taskId:task.taskId}, caps)).toThrow('Unknown');
      principal = 'reader-a';
      tasks.dispatch('tasks/update', {taskId:task.taskId,inputResponses:{details:{action:'decline'}}}, caps);
      expect(tasks.dispatch('tasks/get', {taskId:task.taskId}, caps).status).toBe('cancelled');
      expect(() => tasks.dispatch('tasks/get', {taskId:task.taskId}, {})).toThrow('capability');
    } finally { tasks.close(); rmSync(folder, {recursive:true,force:true}); }
  });

  it('freezes reviewed arguments and cannot turn a declined proposal into a write', async () => {
    await inMemory(notesServer, async client => {
      const proposal = {name:'notes__create_note',arguments:{title:'Reviewed',body:'Original'}};
      const host = new CourseHost(new Map([['notes',client]]), async () => {
        proposal.arguments.title = 'Changed after review'; return true;
      });
      await host.execute(proposal);
      const found = await client.callTool({name:'search_notes',arguments:{query:'Reviewed'}});
      expect(JSON.stringify(found)).toContain('Reviewed');
      const denied = new CourseHost(new Map([['notes',client]]), async () => false);
      await expect(denied.execute({name:'notes__create_note',arguments:{title:'Forbidden',body:'x',confirmed:true}})).rejects.toThrow('Invalid arguments');
      await expect(denied.execute({name:'notes__create_note',arguments:{title:'Forbidden',body:'x'}})).rejects.toThrow('declined');
      const absent = await client.callTool({name:'search_notes',arguments:{query:'Forbidden'}});
      expect(absent.structuredContent).toEqual({result:[]});
    });
  });

  it('requires Origin/CSRF checks and consumes each web approval exactly once', async () => {
    const app = await webHost(0);
    if (!app.server.listening) await once(app.server, 'listening');
    const address = app.server.address();
    if (!address || typeof address === 'string') throw new Error('No local address');
    const base = `http://127.0.0.1:${address.port}`;
    try {
      const html = await (await fetch(base)).text();
      const token = /const token="([^"]+)"/.exec(html)?.[1];
      expect(token).toBeTruthy();
      expect((await fetch(base+'/api/tools')).status).toBe(403);
      expect((await fetch(base+'/api/tools',{headers:{Origin:'https://untrusted.example','X-CSRF-Token':token!}})).status).toBe(403);
      const post = (route:string,body:unknown) => fetch(base+'/api/'+route,{method:'POST',headers:{'X-CSRF-Token':token!,'Content-Type':'application/json',Origin:base},body:JSON.stringify(body)});
      const proposal = await (await post('propose',{name:'notes__create_note',arguments:{title:'Web review',body:'Reviewed'}})).json();
      expect((await post('approve',{ticket:proposal.ticket})).status).toBe(200);
      expect((await post('approve',{ticket:proposal.ticket})).status).toBe(400);
      const declined = await (await post('propose',{name:'notes__create_note',arguments:{title:'Declined',body:'No write'}})).json();
      expect((await post('decline',{ticket:declined.ticket})).status).toBe(200);
      expect((await post('approve',{ticket:declined.ticket})).status).toBe(400);
    } finally { await app.close(); }
  }, 15000);
});
