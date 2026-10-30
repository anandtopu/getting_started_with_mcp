/** SDK-free stdio client for module 01. Keeps IDs, deadlines and framing visible. */
import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';
import { resolve } from 'node:path';
import { strict as assert } from 'node:assert';
import { root } from './data.ts';

export async function rawLesson() {
  const child=spawn(process.execPath,['--import','tsx',resolve(root,'modules/01_architecture_wire/typescript/raw_server.ts')],{cwd:root,stdio:['pipe','pipe','pipe']});
  child.stderr.resume();
  const pending=new Map<number,{resolve:(value:Record<string,unknown>)=>void;reject:(error:Error)=>void;timer:ReturnType<typeof setTimeout>}>();
  const lines=createInterface({input:child.stdout});let sequence=0;
  const rejectAll=()=>{for(const item of pending.values()){clearTimeout(item.timer);item.reject(new Error('Raw server closed'));}pending.clear();};
  child.on('error',rejectAll);child.on('exit',rejectAll);
  lines.on('line',line=>{
    try {
      const message=JSON.parse(line);const item=pending.get(message.id);if(!item)return;
      pending.delete(message.id);clearTimeout(item.timer);
      if(message.error)item.reject(new Error(message.error.message));else item.resolve(message.result);
    }catch{rejectAll();}
  });
  function request(method:string,args:Record<string,unknown>={},version='2026-07-28'):Promise<Record<string,unknown>> {
    const id=++sequence;
    return new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>{pending.delete(id);reject(new Error('Raw request timeout'));},5000);
      pending.set(id,{resolve,reject,timer});
      child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params:{...args,_meta:{'io.modelcontextprotocol/protocolVersion':version,'io.modelcontextprotocol/clientInfo':{name:'Lumen raw client',version:'1'},'io.modelcontextprotocol/clientCapabilities':{}}}})+'\n',error=>{if(error){clearTimeout(timer);pending.delete(id);reject(error);}});
    });
  }
  try {
    const listing=await request('tools/list');assert.equal((listing.tools as {name:string}[])[0].name,'directory_count');
    const result=await request('tools/call',{name:'directory_count',arguments:{}});assert.deepEqual(result.structuredContent,{count:80});
    await assert.rejects(request('unknown'),/Unknown/);
    await assert.rejects(request('tools/call',{name:'directory_count',arguments:[]}),/invalid arguments/);
    await assert.rejects(request('tools/list',{},'invalid'),/Unsupported protocol/);
  }finally{lines.close();child.stdin.end();if(child.exitCode===null)child.kill();rejectAll();}
}
