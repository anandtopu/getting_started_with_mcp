/** Named queries and bounded HTTP: the native counterpart of Python module 07. */
import { DatabaseSync } from 'node:sqlite';
import { resolve } from 'node:path';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { McpServer, ResourceTemplate } from '@modelcontextprotocol/server';
import { z } from 'zod';
import { root } from './data.ts';
import { read, structured, failure } from './notes.ts';

const pageArgs = z.object({
  start:z.iso.date().default('2025-08-01'),
  offset:z.number().int().min(0).max(365).default(0),
  limit:z.number().int().min(1).max(50).default(10),
});

export function usagePage(input:unknown) {
  const {start,offset,limit}=pageArgs.parse(input);
  const db=new DatabaseSync(resolve(root,'data/analytics.db'),{readOnly:true});
  try {
    db.exec('PRAGMA query_only=ON');
    // A fixed indexed-table query over 365 fixture rows bounds computation.
    // No arbitrary SQL is accepted. Production data needs its own query deadline.
    const rows=db.prepare('SELECT * FROM daily_usage WHERE day>=? ORDER BY day LIMIT ? OFFSET ?').all(start,limit+1,offset);
    return {rows:rows.slice(0,limit),truncated:rows.length>limit,next_offset:rows.length>limit?offset+limit:null};
  } finally {db.close();}
}

export async function fetchObject(url:URL, fetcher:typeof fetch=fetch) {
  const response=await fetcher(url,{signal:AbortSignal.timeout(5000),redirect:'error'});
  if(!response.ok || !response.body) throw new Error('API request failed; check the project or retry later.');
  const reader=response.body.getReader(); const chunks:Uint8Array[]=[]; let size=0;
  try {
    while(true) {
      const next=await reader.read(); if(next.done)break;
      size+=next.value.byteLength;
      if(size>64000)throw new Error('API response exceeds 64 KB; request less data.');
      chunks.push(next.value);
    }
    const value:unknown=JSON.parse(Buffer.concat(chunks).toString('utf8'));
    if(!value || typeof value!=='object' || Array.isArray(value))throw new Error('API response must be an object.');
    return value as Record<string,unknown>;
  } finally {await reader.cancel();reader.releaseLock();}
}

export function realDataServer(internalOrigin?:string, fetcher:typeof fetch=fetch) {
  const server=new McpServer({name:'Lumen TypeScript real data',version:'1'});
  server.registerTool('analytics_page',{description:'Read a bounded daily-usage page; follow its link for more.',inputSchema:pageArgs,annotations:read},args=>{
    const page=usagePage(args);
    return {...structured(page),content:[
      {type:'text' as const,text:JSON.stringify(page)},
      ...(page.next_offset===null?[]:[{type:'resource_link' as const,name:'Next usage page',uri:`analytics://usage/${args.start}/${page.next_offset}/${args.limit}`,mimeType:'application/json'}]),
    ]};
  });
  server.registerResource('usage',new ResourceTemplate('analytics://usage/{start}/{offset}/{limit}',{list:undefined}),{mimeType:'application/json'},(uri,args)=>({contents:[{uri:uri.href,mimeType:'application/json',text:JSON.stringify(usagePage({start:args.start,offset:Number(args.offset),limit:Number(args.limit)}))}]}));
  server.registerTool('project_details',{description:'Read a project from the configured local internal-API fixture.',inputSchema:z.object({project_id:z.number().int().min(1).max(5)}),annotations:read},async args=>{
    if(!internalOrigin)return failure('Start the local API use case before requesting project details.');
    return structured(await fetchObject(new URL(`/projects/${args.project_id}`,internalOrigin),fetcher));
  });
  server.registerTool('weather',{description:'Explicitly opt in to reading Open-Meteo for these coordinates.',inputSchema:z.object({latitude:z.number().min(-90).max(90),longitude:z.number().min(-180).max(180),allow_network:z.boolean().default(false)}),annotations:{...read,openWorldHint:true}},async args=>{
    if(!args.allow_network)return failure('External network is off; explicitly set allow_network=true.');
    const url=new URL('https://api.open-meteo.com/v1/forecast');
    url.search=new URLSearchParams({latitude:String(args.latitude),longitude:String(args.longitude),current:'temperature_2m'}).toString();
    return structured(await fetchObject(url,fetcher));
  });
  return server;
}

export async function startInternalAPI() {
  const server=createServer((req,res)=>{
    const address=server.address();const port=address && typeof address==='object'?address.port:0;
    if(req.headers.host!==`127.0.0.1:${port}` || req.headers.origin){res.writeHead(403).end();return;}
    const id=Number(/^\/projects\/([1-5])$/.exec(req.url??'')?.[1]);
    if(req.method!=='GET' || !id){res.writeHead(404).end();return;}
    res.writeHead(200,{'Content-Type':'application/json'}).end(JSON.stringify({id,name:`Lumen project ${id}`,service:'local fixture'}));
  });
  server.listen(0,'127.0.0.1');await once(server,'listening');
  const address=server.address();if(!address || typeof address==='string')throw new Error('No local API address');
  return { origin: `http://127.0.0.1:${address.port}`, close: async () => { server.closeAllConnections(); await new Promise<void>(done => server.close(() => done())); } };
}

export async function withInternalAPI<T>(action:(origin:string)=>Promise<T>) {
  const api = await startInternalAPI();
  try { return await action(api.origin); } finally { await api.close(); }
}
