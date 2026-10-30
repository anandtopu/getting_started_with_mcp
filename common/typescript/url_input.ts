/** URL input needs browser completion as well as an accepted MCP answer. */
import { createServer } from 'node:http';
import { once } from 'node:events';
import { randomBytes } from 'node:crypto';
import { McpServer, inputRequired } from '@modelcontextprotocol/server';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { Client, InMemoryTransport } from '@modelcontextprotocol/client';
import { z } from 'zod';
import { strict as assert } from 'node:assert';
import { structured, write, failure } from './notes.ts';

export async function urlInputDemo(browserCompletes:boolean) {
  const grants=new Map<string,{binding:string;expires:number;approved:boolean;csrf:string}>();
  const portal=createServer(async(req,res)=>{
    const address=portal.address();const port=typeof address==='object'&&address?address.port:0;
    const origin=`http://127.0.0.1:${port}`;
    res.setHeader('Referrer-Policy','no-referrer');res.setHeader('Cache-Control','no-store');
    res.setHeader('Content-Security-Policy',"default-src 'none'; form-action 'self'; frame-ancestors 'none'");
    if(req.headers.host!==`127.0.0.1:${port}` || (req.headers.origin && req.headers.origin!==origin)){res.writeHead(403).end();return;}
    const key=/^\/approve\/([A-Za-z0-9_-]+)$/.exec(req.url??'')?.[1];const grant=key?grants.get(key):undefined;
    if(!grant || grant.expires<=Date.now()){res.writeHead(404).end();return;}
    if(req.method==='GET') {res.writeHead(200,{'Content-Type':'text/html'}).end(`<h1>Export the synthetic report?</h1><form method="post"><input type="hidden" name="csrf" value="${grant.csrf}"><button>Approve export</button></form>`);return;}
    if(req.method!=='POST'){res.writeHead(405).end();return;}
    let body='';for await(const chunk of req){body+=chunk;if(Buffer.byteLength(body)>1024){res.writeHead(413).end();return;}}
    if(new URLSearchParams(body).get('csrf')!==grant.csrf){res.writeHead(403).end();return;}
    grant.approved=true;res.writeHead(200).end('Approved. Return to the host.');
  });
  portal.listen(0,'127.0.0.1');await once(portal,'listening');
  const address=portal.address();if(!address || typeof address==='string')throw new Error('No portal port');
  const origin=`http://127.0.0.1:${address.port}`;
  const factory=()=>{
    const server=new McpServer({name:'Lumen URL input',version:'1'});
    server.registerTool('export_report',{description:'Approve a synthetic export in a separate local browser.',inputSchema:z.object({report:z.literal('synthetic').default('synthetic')}),annotations:write},({report},ctx)=>{
      const state=ctx.mcpReq.requestState<string>();
      if(!state) {
        for(const [key,grant]of grants)if(grant.expires<=Date.now())grants.delete(key);
        if(grants.size>=20)return failure('Approval capacity reached.');
        const key=randomBytes(24).toString('base64url');grants.set(key,{binding:report,expires:Date.now()+60000,approved:false,csrf:randomBytes(24).toString('base64url')});
        return inputRequired({requestState:key,inputRequests:{decision:inputRequired.elicitUrl({message:'Approve the export in this local page, then return.',url:`${origin}/approve/${key}`})}});
      }
      const grant=grants.get(state);grants.delete(state);
      if(!grant || grant.binding!==report || grant.expires<=Date.now())return failure('Unknown, changed or expired approval.');
      const answer=z.object({action:z.enum(['accept','decline','cancel'])}).safeParse(ctx.mcpReq.inputResponses?.decision);
      if(!answer.success || answer.data.action!=='accept')return structured({exported:false});
      if(!grant.approved)return failure('Browser approval has not completed; start again.');
      return structured({exported:true,report});
    });
    return server;
  };
  const [left,right]=InMemoryTransport.createLinkedPair();const handle=serveStdio(factory,{transport:left});
  const client=new Client({name:'Lumen URL host fixture',version:'1'},{versionNegotiation:{mode:{pin:'2026-07-28'}},capabilities:{elicitation:{url:{}}}});
  client.setRequestHandler('elicitation/create',async request=>{
    if(request.params.mode!=='url')return {action:'decline'};
    const url=new URL(request.params.url);assert.equal(url.origin,origin);
    if(browserCompletes) {
      const page=await (await fetch(url,{redirect:'error',signal:AbortSignal.timeout(3000)})).text();
      const csrf=/name="csrf" value="([A-Za-z0-9_-]+)"/.exec(page)![1];
      assert.equal((await fetch(url,{method:'POST',headers:{Origin:'https://untrusted.example'},body:new URLSearchParams({csrf})})).status,403);
      assert.equal((await fetch(url,{method:'POST',headers:{Origin:origin},body:new URLSearchParams({csrf}),signal:AbortSignal.timeout(3000)})).status,200);
    }
    // This fixture simulates a user. A real host must open the page for the human.
    return {action:'accept'};
  });
  try {
    await client.connect(right);await client.discover();
    const result=await client.callTool({name:'export_report',arguments:{}});
    assert.equal(result.isError===true,!browserCompletes);
    if(browserCompletes)assert.equal((result.structuredContent as {exported:boolean}).exported,true);
    assert.equal(grants.size,0,'A retry consumes its grant, including failed attempts.');
  }finally{await client.close();await handle.close();portal.closeAllConnections();await new Promise<void>(done=>portal.close(()=>done()));}
}
