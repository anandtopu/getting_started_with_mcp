/** SDK-free newline JSON-RPC server; inspect every byte with wiretap.py.
 * Run: node --import tsx modules/01_architecture_wire/typescript/raw_server.ts
 * Expected: waits silently; tools/list advertises directory_count.
 * Spec: https://modelcontextprotocol.io/specification/2026-07-28
 * Capture: uv run python scripts/phase8.py --capture
 */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { root } from '../../../common/typescript/data.ts';

const prefix='io.modelcontextprotocol/';
const tool={name:'directory_count',description:'Count the synthetic employee directory.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true,destructiveHint:false,idempotentHint:true,openWorldHint:false}};
let pending='';
function dispatch(line:string) {
  let id:unknown=null;
  const send=(value:object)=>process.stdout.write(JSON.stringify({jsonrpc:'2.0',id,...value})+'\n');
  let request;
  try {request=JSON.parse(line);}catch {send({error:{code:-32700,message:'Parse error'}});return;}
  if(!request || Array.isArray(request) || request.jsonrpc!=='2.0' || typeof request.method!=='string') {send({error:{code:-32600,message:'Invalid Request'}});return;}
  if(!('id' in request))return; // Notifications receive no response.
  id=request.id;
  if(typeof id!=='number' && typeof id!=='string'){id=null;send({error:{code:-32600,message:'Invalid ID'}});return;}
  const params=request.params===undefined?{}:request.params;
  if(!params || typeof params!=='object' || Array.isArray(params)){send({error:{code:-32602,message:'Invalid Params'}});return;}
  const meta=params._meta===undefined?{}:params._meta;
  if(!meta || typeof meta!=='object' || Array.isArray(meta)){send({error:{code:-32602,message:'Invalid Params'}});return;}
  if(meta[prefix+'protocolVersion']!=='2026-07-28') {send({error:{code:-32022,message:'Unsupported protocol version',data:{supported:['2026-07-28'],requested:meta[prefix+'protocolVersion']??null}}});return;}
  if(!meta[prefix+'clientCapabilities'] || typeof meta[prefix+'clientCapabilities']!=='object' || Array.isArray(meta[prefix+'clientCapabilities'])) {send({error:{code:-32602,message:'Client capabilities must be an object'}});return;}
  let result;
  if(request.method==='server/discover')result={supportedVersions:['2026-07-28'],capabilities:{tools:{}},ttlMs:0,cacheScope:'private'};
  else if(request.method==='tools/list')result={tools:[tool],ttlMs:0,cacheScope:'private'};
  else if(request.method==='tools/call' && params.name==='directory_count' && params.arguments && typeof params.arguments==='object' && !Array.isArray(params.arguments) && Object.keys(params.arguments).length===0) {
    const count=JSON.parse(readFileSync(resolve(root,'data/directory/employees.json'),'utf8')).length;
    result={content:[{type:'text',text:String(count)}],structuredContent:{count}};
  }else {send({error:{code:request.method==='tools/call'?-32602:-32601,message:'Unknown method or invalid arguments'}});return;}
  // KEY IDEA: correlation and the current envelope are explicit, without SDK code.
  send({result:{...result,resultType:'complete',_meta:{[prefix+'serverInfo']:{name:'Lumen raw TypeScript',version:'1'}}}});
}
process.stdin.setEncoding('utf8');
process.stdin.on('data',chunk=>{
  pending+=chunk;
  if(Buffer.byteLength(pending)>64000){process.stderr.write('Input exceeds 64 KB.\n');process.exitCode=1;process.stdin.destroy();return;}
  let end;while((end=pending.indexOf('\n'))>=0){const line=pending.slice(0,end);pending=pending.slice(end+1);dispatch(line);}
});
