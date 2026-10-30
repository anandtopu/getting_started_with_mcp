/** Observe running work, cancellation cleanup, pagination and completions. */
import { strict as assert } from 'node:assert';
import { setTimeout as pause } from 'node:timers/promises';
import { McpServer } from '@modelcontextprotocol/server';
import { inMemory, allResources } from './clients.ts';
import { remoteWorkspace } from './remote.ts';

export async function utilityLesson(part:number) {
  const workspace=remoteWorkspace();
  try {
    await inMemory(workspace.factory,async client=>{
      if(part===1) {
        const progress:number[]=[];
        const result=await client.callTool({name:'quarterly_report',arguments:{quarter:'Q1'}},{onprogress:p=>{progress.push(p.progress);}});
        assert.equal(result.isError===true,false);assert.deepEqual(progress,[1,2,3,4]);
        assert.equal(((await client.callTool({name:'report_status',arguments:{}})).structuredContent as {active:number}).active,0);
      } else if(part===2) {
        const abort=new AbortController();let observed=false;
        await assert.rejects(client.callTool({name:'quarterly_report',arguments:{delay:0.05}},{signal:abort.signal,onprogress:()=>{observed=true;abort.abort();}}));
        assert.ok(observed,'Cancel a running operation, not an already-aborted request.');
        let active=1;
        for(let attempt=0;attempt<20 && active;attempt++) {
          await pause(10);
          active=Number(((await client.callTool({name:'report_status',arguments:{}})).structuredContent as {active:number}).active);
        }
        assert.equal(active,0,'Cancellation must release server-owned work.');
      } else {
        const result=await client.complete({ref:{type:'ref/prompt',name:'report_brief'},argument:{name:'quarter',value:'Q'}});
        assert.deepEqual(result.completion.values,['Q1','Q2','Q3','Q4']);
      }
    });
  } finally {workspace.close();}
  if(part===3) {
    await inMemory(()=>{
      const server=new McpServer({name:'Lumen paged resources',version:'1'},{capabilities:{resources:{}}});
      server.server.setRequestHandler('resources/list',request=>{
        const cursor=request.params?.cursor;
        if(cursor===undefined)return {resources:[],nextCursor:'last'};
        if(cursor==='last')return {resources:[{uri:'wiki://index',name:'Wiki index'}]};
        throw new Error('Invalid cursor; restart discovery.');
      });
      return server;
    },async client=>{
      assert.equal((await allResources(client)).length,1);
      await assert.rejects(client.listResources({cursor:'untrusted'}),/Invalid cursor/);
    });
  }
}
