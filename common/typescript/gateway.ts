/** Per-call policy, namespaced discovery and redacted audit for fixed upstreams. */
import { McpServer } from '@modelcontextprotocol/server';
import type { Client, Tool } from '@modelcontextprotocol/client';
import { CourseHost, fingerprint, type Proposal } from './advanced_host.ts';
import { RateLimit } from './advanced_policy.ts';

export type Identity = {subject:string; scopes:string[]};
export class Gateway {
  readonly disabled = new Set<string>();
  readonly audit:{subject:string;tool:string;outcome:string}[]=[];
  readonly host:CourseHost;
  constructor(clients:Map<string,Client>, readonly identity:()=>Identity, readonly limit=new RateLimit()) {
    this.host=new CourseHost(clients, async()=>true);
  }
  async catalog():Promise<Tool[]> {
    const {scopes}=this.identity();
    return (await this.host.catalog()).filter(t=>!this.disabled.has(t.name.split('__')[0]) && scopes.includes('workspace:read') && (t.annotations?.readOnlyHint===true || scopes.includes('workspace:write')));
  }
  async call(proposal:Proposal, signal?:AbortSignal) {
    const identity=this.identity();
    let outcome='denied';
    try {
      const tool=(await this.catalog()).find(t=>t.name===proposal.name);
      if(!tool) throw new Error('Tool not available');
      if(!this.limit.allow(identity.subject)) throw new Error('Rate limit reached');
      if(tool.annotations?.readOnlyHint!==true && proposal.arguments.confirmed!==true) throw new Error('Confirmation required');
      const current=(await this.catalog()).find(t=>t.name===proposal.name);
      if(!current || fingerprint(current)!==fingerprint(tool)) throw new Error('Tool changed');
      const [alias,...name]=proposal.name.split('__');
      signal?.throwIfAborted();
      const result=await this.host.clients.get(alias)!.callTool({name:name.join('__'),arguments:structuredClone(proposal.arguments)},{timeout:5000,signal});
      outcome=result.isError?'tool_error':'allowed';return result;
    } finally {
      this.audit.push({subject:identity.subject,tool:proposal.name,outcome});
      if(this.audit.length>100) this.audit.shift();
    }
  }
  server() {
    const server=new McpServer({name:'Lumen TypeScript gateway',version:'1.0'},{capabilities:{tools:{}}});
    server.server.setRequestHandler('tools/list',async()=>({tools:await this.catalog(),ttlMs:0,cacheScope:'private' as const}));
    server.server.setRequestHandler('tools/call',async (req,ctx)=>this.call({name:req.params.name,arguments:req.params.arguments??{}},ctx.mcpReq.signal));
    return server;
  }
}
