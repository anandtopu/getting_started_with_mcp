/** Fixed-profile connection ownership; retry only locally allowlisted reads. */
import { Client, type Tool } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';
import { resolve } from 'node:path';
import { root } from './data.ts';
import { fingerprint } from './advanced_host.ts';

export class Connection {
  client?:Client;
  private reviewed=new Map<string,string>();
  private connectPromise?:Promise<Client>;
  constructor(readonly profile:'notes'|'workflow'='notes',readonly legacy=false) {}
  connect():Promise<Client> {
    if(this.client) return Promise.resolve(this.client);
    if(this.connectPromise) return this.connectPromise;
    this.connectPromise=this.open().finally(()=>{this.connectPromise=undefined;});return this.connectPromise;
  }
  private async open() {
    const client=new Client({name:'Lumen TS production host',version:'1'},{versionNegotiation:{mode:this.legacy?'auto':{pin:'2026-07-28'}}});
    try {
      await client.connect(new StdioClientTransport({command:process.execPath,args:['--import','tsx',resolve(root,'modules/bonus/B1_typescript_track/typescript/server.ts'),this.profile],cwd:root}),{timeout:5000});
      await client.listTools();this.client=client;return client;
    } catch(error){await client.close();throw error;}
  }
  review(tools:Tool[]) {this.reviewed=new Map(tools.map(t=>[t.name,fingerprint(t)]));}
  async call(name:string,args:Record<string,unknown>) {
    for(let attempt=0;attempt<2;attempt++) {
      const client=await this.connect();
      const tool=(await client.listTools(undefined,{cacheMode:'refresh'})).tools.find(t=>t.name===name);
      if(!tool || this.reviewed.get(name)!==fingerprint(tool)) throw new Error('Review the current catalog first');
      try {return await client.callTool({name,arguments:args},{timeout:3000});}
      catch(error) {
        // This local list, not remote annotations, grants retry permission.
        if(attempt || !['search_notes','triage_week','draft_status'].includes(name) || !(error instanceof Error) || !/closed|timeout|connect/i.test(error.message)) throw error;
        await this.close();
      }
    }
    throw new Error('Reconnect budget exceeded');
  }
  async close(){await this.connectPromise?.catch(()=>undefined);const client=this.client;this.client=undefined;await client?.close();}
}
