/** A small current-protocol peer for studying wire semantics and custom results.
 * The official SDK owns framing; this deliberately limited peer owns correlation.
 * It does not implement subscriptions, HTTP authorization or a production host.
 */
import { type Transport, type JSONRPCMessage, type ClientCapabilities } from '@modelcontextprotocol/client';
const prefix='io.modelcontextprotocol/';
export class RpcPeer {
  private next=0;
  private pending=new Map<number,{resolve:(v:Record<string,unknown>)=>void;reject:(e:Error)=>void;timer:ReturnType<typeof setTimeout>}>();
  constructor(readonly transport:Transport,readonly capabilities:ClientCapabilities={}) {}
  async start() {
    this.transport.onmessage=message=>{
      if(!('id' in message) || typeof message.id!=='number') return;
      const p=this.pending.get(message.id);if(!p) return;
      this.pending.delete(message.id);clearTimeout(p.timer);
      if('error' in message) p.reject(new Error(message.error.message));
      else if('result' in message) p.resolve(message.result);
    };
    this.transport.onclose=()=>{for(const p of this.pending.values()){clearTimeout(p.timer);p.reject(new Error('Connection closed'));}this.pending.clear();};
    await this.transport.start();
  }
  request(method:string,params:Record<string,unknown>={}):Promise<Record<string,unknown>> {
    if(this.pending.size>=20) return Promise.reject(new Error('Request budget exceeded'));
    const id=++this.next;
    return new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>{this.pending.delete(id);reject(new Error('Request timeout'));},5000);
      this.pending.set(id,{resolve,reject,timer});
      this.transport.send({jsonrpc:'2.0',id,method,params:{...params,_meta:{[prefix+'protocolVersion']:'2026-07-28',[prefix+'clientInfo']:{name:'Lumen raw TS client',version:'1'},[prefix+'clientCapabilities']:this.capabilities}}}).catch(e=>{clearTimeout(timer);this.pending.delete(id);reject(e);});
    });
  }
  async close(){await this.transport.close();this.transport.onclose?.();}
}
export async function serveRaw(transport:Transport, dispatch:(method:string,params:Record<string,unknown>,caps:ClientCapabilities)=>Record<string,unknown>) {
  transport.onmessage=async (message:JSONRPCMessage)=>{
    if(!('method' in message) || !('id' in message)) return;
    const p=message.params??{};const meta=p._meta??{};
    try {
      if(meta[prefix+'protocolVersion']!=='2026-07-28') {
        await transport.send({jsonrpc:'2.0',id:message.id,error:{code:-32022,message:'Unsupported protocol version',data:{supported:['2026-07-28'],requested:meta[prefix+'protocolVersion']??null}}});return;
      }
      const caps=meta[prefix+'clientCapabilities'];
      if(!caps || typeof caps!=='object' || Array.isArray(caps)) throw new Error('Client capabilities must be an object');
      const result=dispatch(message.method,p,caps as ClientCapabilities);
      await transport.send({jsonrpc:'2.0',id:message.id,result:{resultType:'complete',...result,_meta:{[prefix+'serverInfo']:{name:'Lumen raw TypeScript',version:'1'}}}});
    } catch(e) {await transport.send({jsonrpc:'2.0',id:message.id,error:{code:e instanceof Error && e.message==='Unknown method'?-32601:-32602,message:e instanceof Error?e.message:'Invalid Params'}});}
  };
  await transport.start();
}
