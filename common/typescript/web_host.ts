/** Native local web shell over two fixed MCP servers. Run: node --import tsx common/typescript/web_host.ts */
import { createServer } from 'node:http';
import { randomBytes } from 'node:crypto';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { CourseHost, fingerprint, type Proposal } from './advanced_host.ts';
import { Connection } from './production_host.ts';

export async function webHost(port=8767) {
  const connections=[new Connection('notes'),new Connection('workflow')];
  const clients=await Promise.all(connections.map(c=>c.connect()));
  const csrf=randomBytes(24).toString('base64url');
  const pending=new Map<string,{proposal:Proposal;signature:string;expires:number}>();
  const host=new CourseHost(new Map([['notes',clients[0]],['workflow',clients[1]]]),async()=>true);
  const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Lumen TypeScript host</title><style>body{font:18px system-ui;max-width:52rem;margin:3rem auto;padding:1rem}button,textarea,select{font:inherit;margin:.5rem 0;padding:.6rem}textarea{display:block;width:95%}pre{white-space:pre-wrap}</style><h1>Lumen TypeScript host</h1><p>Choose a tool from two local servers. Review its exact arguments before allowing the call. Data is synthetic.</p><label>Tool <select id="tools"></select></label><label>Arguments<textarea id="args">{"query":"release"}</textarea></label><button id="review">Review</button><pre id="proposal"></pre><button id="approve" disabled>Approve this call</button><button id="decline">Decline</button><pre id="result" role="status"></pre><script nonce="${csrf}">const token=${JSON.stringify(csrf)};let ticket;const el=id=>document.getElementById(id);async function api(path,body){const r=await fetch('/api/'+path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json','X-CSRF-Token':token},body:body?JSON.stringify(body):undefined});const v=await r.json();if(!r.ok)throw Error(v.error);return v;}api('tools').then(v=>{for(const t of v){const o=document.createElement('option');o.value=t.name;o.textContent=t.name;el('tools').append(o);}});el('review').onclick=async()=>{try{const p={name:el('tools').value,arguments:JSON.parse(el('args').value)};const r=await api('propose',p);ticket=r.ticket;el('proposal').textContent=JSON.stringify(p,null,2);el('approve').disabled=false;}catch(e){el('result').textContent=e.message;}};el('approve').onclick=async()=>{el('approve').disabled=true;try{el('result').textContent=JSON.stringify(await api('approve',{ticket}),null,2);}catch(e){el('result').textContent=e.message;}};el('decline').onclick=async()=>{if(ticket)await api('decline',{ticket});ticket=undefined;el('approve').disabled=true;el('proposal').textContent='Declined; no call sent.';};</script></html>`;
  const server=createServer(async(req,res)=>{
    const address=server.address();const actual=typeof address==='object'&&address?address.port:port;
    const respond=(status:number,data:unknown)=>{res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'}).end(JSON.stringify(data));};
    if(![`127.0.0.1:${actual}`,`localhost:${actual}`].includes(req.headers.host??'')){respond(421,{error:'Invalid Host'});return;}
    if(req.headers.origin && ![`http://127.0.0.1:${actual}`,`http://localhost:${actual}`].includes(req.headers.origin)){respond(403,{error:'Invalid Origin'});return;}
    if(req.method==='GET'&&req.url==='/'){res.writeHead(200,{'Content-Type':'text/html','Cache-Control':'no-store','Content-Security-Policy':`default-src 'none'; script-src 'nonce-${csrf}'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'`}).end(html);return;}
    if(req.headers['x-csrf-token']!==csrf){respond(403,{error:'Missing request token'});return;}
    try {
      if(req.method==='GET'&&req.url==='/api/tools'){respond(200,await host.catalog());return;}
      if(req.method!=='POST'){respond(404,{error:'Unknown route'});return;}
      let body='';for await(const chunk of req){body+=chunk;if(Buffer.byteLength(body)>16000){respond(413,{error:'Request too large'});return;}}
      const value=JSON.parse(body);
      for(const [key,p]of pending)if(p.expires<Date.now())pending.delete(key);
      if(req.url==='/api/propose') {
        if(pending.size>=20)throw new Error('Review capacity reached');
        if(typeof value.name!=='string'||!value.arguments||typeof value.arguments!=='object'||Array.isArray(value.arguments))throw new Error('Invalid proposal');
        const tool=(await host.catalog()).find(t=>t.name===value.name);if(!tool)throw new Error('Unknown tool');
        const ticket=randomBytes(24).toString('base64url');pending.set(ticket,{proposal:structuredClone(value),signature:fingerprint(tool),expires:Date.now()+60000});respond(200,{ticket});return;
      }
      if(!['/api/approve','/api/decline'].includes(req.url??'')){respond(404,{error:'Unknown route'});return;}
      const proposal=pending.get(value.ticket);pending.delete(value.ticket);
      if(!proposal)throw new Error('Unknown or expired review');
      const current=(await host.catalog()).find(t=>t.name===proposal.proposal.name);
      if(!current || fingerprint(current)!==proposal.signature)throw new Error('Tool changed; review again');
      respond(200,req.url==='/api/approve'?await host.execute(proposal.proposal):{declined:true});
    }catch(error){respond(400,{error:error instanceof Error?error.message:'Request failed'});}
  });
  server.listen(port,'127.0.0.1');
  return {server,close:async()=>{await new Promise<void>(resolve=>server.close(()=>resolve()));await Promise.all(connections.map(c=>c.close()));}};
}
if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const app=await webHost();console.log('Open http://127.0.0.1:8767');
  process.on('SIGINT',async()=>{await app.close();});process.on('SIGTERM',async()=>{await app.close();});
}
