/** Executable TypeScript counterparts. Each named case makes an independent assertion. */
import { strict as assert } from 'node:assert';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { Client, InMemoryTransport } from '@modelcontextprotocol/client';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { inMemory } from './clients.ts';
import { root, employees, safePath } from './data.ts';
import { notesServer, configuredNotesServer } from './notes.ts';
import { remoteWorkspace } from './remote.ts';
import { withRemote, headerLab } from './remote_client.ts';
import { CourseHost, fakeModel, providerTools } from './advanced_host.ts';
import { fixtureKeys, mintToken, verifyToken, ReviewLedger, RateLimit, redact, publicEndpoint } from './advanced_policy.ts';
import { advancedServer } from './advanced_server.ts';
import { realDataServer, withInternalAPI } from './real_data.ts';
import { utilityLesson } from './utilities.ts';
import { mirrorServer, taskToolsServer, designEvaluation } from './tool_design.ts';
import { validateMetadata, registryPages } from './registry.ts';
import { traces, load, evaluate, validateStdout } from './quality.ts';

import { Gateway } from './gateway.ts';
import { taskDemo } from './task_receiver.ts';
import { appDemo } from './app_bridge.ts';
import { Connection } from './production_host.ts';
import { rawLesson } from './raw_client.ts';
import { urlInputDemo } from './url_input.ts';

export const modules=[0,1,6,7,8,9,11,12,13,14,15,16,17,18,19,20,21];

export async function lesson(module:number, part:number) {
  if(!modules.includes(module) || ![1,2,3].includes(part)) throw new Error('Unknown lesson');
  if(module===0) {
    if(part===1) assert.equal(employees().length,80);
    if(part===2) assert.equal(JSON.parse(readFileSync(resolve(root,'node_modules/@modelcontextprotocol/server/package.json'),'utf8')).version,'2.4.0');
    if(part===3) await inMemory(notesServer,async c=>assert.ok((await c.listTools()).tools.some(t=>t.name==='search_notes')));
  } else if(module===1) {
    if(part===1) await rawLesson();
    if(part===2) await inMemory(notesServer,async c=>assert.ok((await c.discover()).capabilities.tools));
    if(part===3) await inMemory(notesServer,async c=>assert.equal((await c.callTool({name:'search_notes',arguments:{query:'release'}})).isError===true,false));
  } else if(module===6) {
    await inMemory(notesServer,async c=>{
      const host=new CourseHost(new Map([['notes',c]]),async()=>part!==2);
      const call={name:'notes__search_notes',arguments:{query:'release'}};
      if(part===1) assert.equal((await host.run(fakeModel(call),'Find release notes')).calls,1);
      if(part===2) await assert.rejects(host.execute(call),/declined/);
      if(part===3) for(const provider of ['openai','anthropic','gemini','ollama'] as const) assert.ok(providerTools(await host.catalog(),provider).length);
    });
  } else if(module===7) {
    if(part===1) {
      const workspace=remoteWorkspace();
      try {await inMemory(workspace.factory,async c=>{
        const args={issue:{title:'Reviewed'},operation_key:'once'};
        assert.equal((await c.callTool({name:'create_issue',arguments:args})).isError,true);
        const created=await c.callTool({name:'create_issue',arguments:{...args,confirmed:true}});
        const repeated=await c.callTool({name:'create_issue',arguments:{...args,confirmed:true}});
        assert.deepEqual(created.structuredContent,repeated.structuredContent);
        const id=(created.structuredContent as {id:number}).id;
        assert.equal((await c.callTool({name:'update_issue',arguments:{issue_id:id,status:'closed',confirmed:true}})).isError===true,false);
        await c.callTool({name:'delete_issue',arguments:{issue_id:id,confirmed:true}});
        assert.equal((await c.callTool({name:'read_issue',arguments:{issue_id:id}})).isError,true);
        assert.equal((await c.callTool({name:'create_issue',arguments:{...args,confirmed:true}})).isError,true);
      });}finally{workspace.close();}
    }
    if(part===2) await inMemory(realDataServer,async c=>{
      const result=await c.callTool({name:'analytics_page',arguments:{limit:2}});
      assert.equal((result.structuredContent as {rows:unknown[]}).rows.length,2);
      const link=result.content.find(v=>v.type==='resource_link');assert.ok(link && link.type==='resource_link');
      const next=await c.readResource({uri:link.uri});assert.ok('text' in next.contents[0] && next.contents[0].text.includes('rows'));
      assert.equal((await c.callTool({name:'analytics_page',arguments:{limit:999}})).isError,true);
    });
    if(part===3) await withInternalAPI(origin=>inMemory(()=>realDataServer(origin),async c=>{
      const result=await c.callTool({name:'project_details',arguments:{project_id:1}});
      assert.equal((result.structuredContent as {name:string}).name,'Lumen project 1');
      assert.equal((await c.callTool({name:'project_details',arguments:{project_id:999}})).isError,true);
      assert.equal((await c.callTool({name:'weather',arguments:{latitude:40,longitude:-90}})).isError,true);
    }));
  } else if(module===8) {
    await utilityLesson(part);
  } else if(module===9) {
    if(part===1) await formDemo(true);
    if(part===2) await formDemo(false);
    if(part===3) {const l=new ReviewLedger();const key=l.issue('reviewed');assert.throws(()=>l.take(key,'changed'));assert.throws(()=>l.take(key,'reviewed'));await urlInputDemo(false);await urlInputDemo(true);}
  } else if(module===11) {
    const keys=fixtureKeys();const now=Date.now()/1000;
    const token=mintToken({iss:'https://auth.lumen.example',aud:'https://ops.lumen.example/mcp',sub:'synthetic-reader',iat:now,exp:now+60,scope:'issues:read'},keys.privateKey);
    if(part===1) assert.equal(verifyToken(token,keys.publicKey,'https://auth.lumen.example','https://ops.lumen.example/mcp').sub,'synthetic-reader');
    if(part===2) assert.throws(()=>verifyToken(token,keys.publicKey,'https://attacker.invalid','https://ops.lumen.example/mcp'));
    if(part===3) assert.throws(()=>verifyToken(token,keys.publicKey,'https://auth.lumen.example','https://ops.lumen.example/mcp',now+61));
  } else if(module===12) {
    if(part===1) assert.throws(()=>safePath(resolve(root,'data/files'),'../issues.db'));
    if(part===2) assert.deepEqual(redact({authorization:'secret',nested:{access_token:'secret'}}),{authorization:'[REDACTED]',nested:{access_token:'[REDACTED]'}});
    if(part===3) assert.throws(()=>publicEndpoint('http://169.254.169.254/mcp'));
  } else if(module===13) {
    await inMemory(advancedServer,async c=>{
      if(part===1) assert.equal((await c.callTool({name:'checked_note',arguments:{text:'release'}})).isError===true,false);
      if(part===2) assert.equal((await c.callTool({name:'checked_note',arguments:{text:'x'.repeat(201)}})).isError,true);
      if(part===2) {assert.throws(()=>validateStdout('debug startup'),/stderr/);assert.equal(validateStdout('{"jsonrpc":"2.0","id":1,"result":{}}'),1);}
    });
    if(part===3) {assert.equal((await traces()).length,3);assert.equal((await load()).requests,10);assert.equal(evaluate().correct,evaluate().total);}
  } else if(module===14) {
    if(part===1) await inMemory(mirrorServer,async c=>assert.equal((await c.listTools()).tools.length,25));
    if(part===2) await inMemory(taskToolsServer,async c=>{
      assert.equal((await c.listTools()).tools.length,6);
      const concise=await c.callTool({name:'issue_brief',arguments:{issue_id:1}});
      const detailed=await c.callTool({name:'issue_brief',arguments:{issue_id:1,mode:'detailed'}});
      assert.ok(JSON.stringify(detailed).length>JSON.stringify(concise).length);
      assert.equal((await c.callTool({name:'issue_brief',arguments:{issue_id:-1}})).isError,true);
    });
    if(part===3) {
      const scores=await designEvaluation();
      for(const name of ['mirror','task_tools'])assert.equal((scores[name] as {completed:number}).completed,6);
    }
  } else if(module===15) {
    const {frameworkDemo}=await import('./frameworks.ts');
    await frameworkDemo((['agents','langchain','langgraph'] as const)[part-1]);
  } else if(module===16) {
    await inMemory(notesServer,async upstream=>{
      let identity={subject:'reader',scopes:['workspace:read']};
      const gw=new Gateway(new Map([['notes',upstream]]),()=>identity,new RateLimit(1));
      if(part===1){assert.ok(!(await gw.catalog()).some(t=>t.name.includes('create_note')));await assert.rejects(gw.call({name:'notes__create_note',arguments:{confirmed:true}}),/not available/);}
      if(part===2){identity={subject:'writer',scopes:['workspace:read','workspace:write']};await assert.rejects(gw.call({name:'notes__create_note',arguments:{title:'x',body:'y'}}),/Confirmation/);assert.equal(gw.audit[0].outcome,'denied');}
      if(part===3){await gw.call({name:'notes__search_notes',arguments:{}});await assert.rejects(gw.call({name:'notes__search_notes',arguments:{}}),/Rate limit/);gw.disabled.add('notes');assert.deepEqual(await gw.catalog(),[]);}
    });
  } else if(module===17) {
    if(part===1) await taskDemo();
    if(part===2) await formDemo(true);
    if(part===3) await appDemo();
  } else if(module===18) {
    if(part===1) await inMemory(()=>configuredNotesServer(true),async c=>assert.deepEqual((await c.listTools()).tools.map(t=>t.name),['search_notes']));
    if(part===2) assert.equal(JSON.parse(readFileSync(resolve(root,'distribution/npm/package.json'),'utf8')).version,'1.0.0');
    if(part===3) {const manifest=JSON.parse(readFileSync(resolve(root,'distribution/mcpb/manifest.json'),'utf8'));assert.equal(manifest.manifest_version,'0.3');assert.equal(manifest.server.type,'node');}
  } else if(module===19) {
    const metadata=validateMetadata();
    if(part===1) assert.ok(metadata.name.startsWith('io.github.anandtopu/'));
    if(part===2) {assert.throws(()=>validateMetadata({name:metadata.name}));assert.throws(()=>validateMetadata({...metadata,version:'99.0.0'}),/identity/);}
    if(part===3) {
      assert.equal((await registryPages(async cursor=>cursor?{servers:[]}:{servers:[metadata],metadata:{nextCursor:'next'}})).length,1);
      await assert.rejects(registryPages(async()=>({servers:[],metadata:{nextCursor:'repeat'}})),/repeated/);
      assert.throws(()=>publicEndpoint('https://user:secret@example.com/mcp'));
    }
  } else if(module===20) {
    if(part===1) await withRemote(headerLab);
    if(part===2) assert.throws(()=>publicEndpoint('http://public.example/mcp'));
    if(part===3) {const limit=new RateLimit(2,()=>100);assert.ok(limit.allow('one'));assert.ok(limit.allow('one'));assert.equal(limit.allow('one'),false);}
  } else if(module===21) {
    const connection=new Connection('notes',part===3);
    try {
      const client=await connection.connect();const tools=(await client.listTools()).tools;
      if(part===2) await assert.rejects(connection.call('search_notes',{}),/Review/);
      else {connection.review(tools);assert.ok(!(await connection.call('search_notes',{query:'release'})).isError);if(part===1){await connection.close();assert.ok(!(await connection.call('search_notes',{})).isError);}}
    } finally {await connection.close();}
  }
  return {module,example:part,status:'PASS'};
}

export async function formDemo(accept:boolean) {
  const [left,right]=InMemoryTransport.createLinkedPair();
  const handle=serveStdio(advancedServer,{transport:left});
  const client=new Client({name:'form-lesson',version:'1'},{versionNegotiation:{mode:{pin:'2026-07-28'}},capabilities:{elicitation:{form:{}}}});
  client.setRequestHandler('elicitation/create',async()=>accept?{action:'accept',content:{approve:true}}:{action:'decline'});
  try {await client.connect(right);await client.discover();const result=await client.callTool({name:'review_bulletin',arguments:{text:'Approved release'}});assert.equal((result.structuredContent as {published:boolean}).published,accept);}
  finally {await client.close();await handle.close();}
}
