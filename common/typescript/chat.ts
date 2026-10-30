/** Native terminal host. Run: node --import tsx common/typescript/chat.ts [--live]
 * Default: an approved fixture read over real stdio; no model service is contacted.
 * Live mode: .env selects the provider/model, and each call requires terminal approval.
 */
import { createInterface } from 'node:readline/promises';
import { stdin, stdout } from 'node:process';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';
import { withServer, newClient } from './clients.ts';
import { root } from './data.ts';
import { CourseHost, fakeModel } from './advanced_host.ts';
import { createModel, modelSettings } from './llm.ts';

const live=process.argv.includes('--live');
if(live && existsSync(resolve(root,'.env')))process.loadEnvFile(resolve(root,'.env'));
const terminal=createInterface({input:stdin,output:stdout});
try {
  const model=live?createModel(modelSettings()):fakeModel({name:'notes__search_notes',arguments:{query:'release'}});
  await withServer('02_first_server_tools',notes=>withServer('03_resources',async wiki=>{
    const files=newClient();
    try {
      await files.connect(new StdioClientTransport({command:process.execPath,args:[resolve(root,'node_modules/@modelcontextprotocol/server-filesystem/dist/index.js'),resolve(root,'data/files')],cwd:root}));
      await files.discover();
      const host=new CourseHost(new Map([['notes',notes],['wiki',wiki],['files',files]]),async proposal=>{
        if(!live)return proposal.name==='notes__search_notes' && proposal.arguments.query==='release';
        console.log('Review:',proposal.name,JSON.stringify(proposal.arguments));
        return (await terminal.question('Allow this exact call? [y/N] ')).toLowerCase()==='y';
      });
      const prompt=live?await terminal.question('Lumen Chat: '):'Find release notes.';
      console.log(await host.run(model,prompt));
    }finally{await files.close();}
  }));
}catch(error){console.error(error instanceof Error?error.message:'Host failed. Run uv run python scripts/check_env.py.');process.exitCode=1;}
finally{terminal.close();}
