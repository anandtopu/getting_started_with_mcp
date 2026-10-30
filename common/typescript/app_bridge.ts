/** Official App/AppBridge lifecycle; only the linked read tool can be invoked. */
import { strict as assert } from 'node:assert';
import { App } from '@modelcontextprotocol/ext-apps';
import { AppBridge } from '@modelcontextprotocol/ext-apps/app-bridge';
import { InMemoryTransport } from '@modelcontextprotocol/client';

export async function appDemo() {
  const app=new App({name:'Lumen analytics',version:'1'}, {}, {autoResize:false});
  const bridge=new AppBridge(null,{name:'Lumen host',version:'1'},{serverTools:{}});
  const result={content:[{type:'text' as const,text:'400 synthetic issues'}],structuredContent:{total:400}};
  bridge.oncalltool=async p=>{if(p.name!=='analytics_dashboard') throw new Error('Tool not allowed');return result;};
  const received=new Promise<unknown>(resolve=>{app.ontoolresult=resolve;});
  let tornDown=false;app.onteardown=async()=>{tornDown=true;return {};};
  const [left,right]=InMemoryTransport.createLinkedPair();
  try {
    await bridge.connect(left);await app.connect(right);await bridge.sendToolResult(result);
    assert.deepEqual(await received,result);
    assert.deepEqual(await app.callServerTool({name:'analytics_dashboard',arguments:{}}),result);
    await assert.rejects(app.callServerTool({name:'create_note',arguments:{}}));
    await bridge.teardownResource({});assert.ok(tornDown);
  } finally {await app.close();await bridge.close();}
}
