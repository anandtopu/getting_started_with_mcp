import { expect, it } from 'vitest';
import { createModel, modelSettings, type ModelSettings } from './llm.ts';
import { CourseHost } from './advanced_host.ts';
import { inMemory } from './clients.ts';
import { notesServer } from './notes.ts';
import { modelTool } from './schemas.ts';

for(const provider of ['openai','anthropic','gemini','ollama'] as const) {
  it(`${provider}: preserves native history and correlates actual MCP results`,async()=>{
    const responses={
      openai:[{output:[{type:'reasoning',id:'reason',encrypted_content:'signature-fixture'},{type:'function_call',call_id:'call-1',name:'notes__search_notes',arguments:'{"query":"release"}'}]},{output:[{type:'message',content:[{type:'output_text',text:'Done'}]}]}],
      anthropic:[{content:[{type:'thinking',thinking:'fixture',signature:'signature-fixture'},{type:'tool_use',id:'call-1',name:'notes__search_notes',input:{query:'release'}}]},{content:[{type:'text',text:'Done'}]}],
      gemini:[{candidates:[{content:{role:'model',parts:[{thoughtSignature:'signature-fixture',functionCall:{id:'call-1',name:'notes__search_notes',args:{query:'release'}}}]}}]},{candidates:[{content:{role:'model',parts:[{text:'Done'}]}}]}],
      ollama:[{message:{role:'assistant',thinking:'signature-fixture',tool_calls:[{function:{name:'notes__search_notes',arguments:{query:'release'}}}]}},{message:{role:'assistant',content:'Done'}}],
    };
    const requests:Record<string,unknown>[]=[];
    const fake:typeof fetch=async(_url,options)=>{
      requests.push(JSON.parse(String(options?.body)));
      expect(options?.redirect).toBe('error');expect(options?.signal).toBeTruthy();
      return Response.json(responses[provider][requests.length-1]);
    };
    const settings:ModelSettings={provider,model:'fixture-model',key:'synthetic-secret',ollamaHost:'http://127.0.0.1:11434'};
    await inMemory(notesServer,async client=>{
      const host=new CourseHost(new Map([['notes',client]]),async()=>true);
      expect(await host.run(createModel(settings,fake),'Find release notes')).toEqual({text:'Done',calls:1});
    });
    expect(requests).toHaveLength(2);
    expect(JSON.stringify(requests[0].tools)).not.toContain('confirmed');
    const history=JSON.stringify(requests[1].input??requests[1].messages??requests[1].contents);
    expect(history).toContain('signature-fixture');expect(history).toContain('Release handover');
    if(provider!=='ollama')expect(history).toContain('call-1');
  });
}

it('keeps provider errors and credentials out of host-visible errors',async()=>{
  const model=createModel({provider:'openai',model:'fixture',key:'synthetic-secret',ollamaHost:'http://127.0.0.1:11434'},async()=>{throw new Error('synthetic-secret private body');});
  await expect(model([{role:'user',content:'Read'}],[])).rejects.toThrow('Tool model request failed for openai.');
});

it('requires explicit live configuration and rejects schema reference attacks',()=>{
  expect(()=>modelSettings({})).toThrow('Choose a live');
  expect(()=>modelSettings({LLM_PROVIDER:'openai',LLM_MODEL:'fixture'})).toThrow('Set the provider');
  for(const schema of [{$ref:'https://untrusted.example/schema'},{$defs:{loop:{$ref:'#/$defs/loop'}},$ref:'#/$defs/loop'}]) {
    expect(()=>modelTool({name:'unsafe',inputSchema:{type:'object',...schema}})).toThrow('local schema');
  }
});

it('validates before asking a human and refuses model-supplied confirmation',async()=>{
  await inMemory(notesServer,async client=>{
    let approvals=0;const host=new CourseHost(new Map([['notes',client]]),async()=>{approvals++;return true;});
    await expect(host.execute({name:'notes__create_note',arguments:{title:'',body:'x'}})).rejects.toThrow('Invalid arguments');
    await expect(host.execute({name:'notes__create_note',arguments:{title:'x',body:'x',confirmed:true}})).rejects.toThrow('Invalid arguments');
    expect(approvals).toBe(0);
  });
});
