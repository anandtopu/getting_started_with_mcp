/** Provider-neutral HTTP adapters. Default lessons use fakeModel; live is opt-in.
 * API contracts and fixture limits: modules/06_building_a_host/typescript/README.md.
 * Preserve native assistant parts, call IDs and thought signatures across turns.
 */
import { z } from 'zod';
import { providerTools, type Model, type Proposal } from './advanced_host.ts';
import { provider as configuredProvider } from './config.ts';
import { publicEndpoint } from './advanced_policy.ts';

type Provider='openai'|'anthropic'|'gemini'|'ollama';
export type ModelSettings={provider:Provider;model:string;key:string;ollamaHost:string};
const object=(value:unknown):Record<string,unknown>=>z.record(z.string(),z.unknown()).parse(value);
const objects=(value:unknown)=>z.array(z.record(z.string(),z.unknown())).parse(value);
const string=(value:unknown)=>z.string().min(1).parse(value);
const proposal=(id:unknown,name:unknown,args:unknown):Proposal=>({id:string(id),name:string(name),arguments:object(args)});

export function modelSettings(env:NodeJS.ProcessEnv=process.env):ModelSettings {
  const provider=configuredProvider(env);
  if(provider==='fake')throw new Error('Choose a live LLM_PROVIDER and LLM_MODEL first. Run uv run python scripts/check_env.py.');
  const key=env[{openai:'OPENAI_API_KEY',anthropic:'ANTHROPIC_API_KEY',gemini:'GEMINI_API_KEY',ollama:''}[provider]??'']??'';
  if(!env.LLM_MODEL || env.LLM_MODEL==='fixture' || (provider!=='ollama' && !key))throw new Error('Set the provider model and key in .env. Run uv run python scripts/check_env.py.');
  return {provider:provider as Provider,model:env.LLM_MODEL,key,ollamaHost:publicEndpoint(env.OLLAMA_HOST??'http://127.0.0.1:11434')};
}

export function createModel(settings:ModelSettings,fetcher:typeof fetch=fetch):Model {
  const native:Record<string,unknown>[]=[];let consumed=0;let turn=0;
  return async (history,tools)=>{
    try {
      if(!native.length) {
        const prompt=string(object(history[0]).content);
        native.push(settings.provider==='gemini'?{role:'user',parts:[{text:prompt}]}:{role:'user',content:prompt});
      }
      const results=history.slice(consumed).map(object).filter(item=>item.role==='tool');
      consumed=history.length;turn++;
      const definitions=providerTools([...tools],settings.provider);
      let url:string;let headers:Record<string,string>={};let body:Record<string,unknown>;
      if(settings.provider==='openai') {
        native.push(...results.map(r=>({type:'function_call_output',call_id:r.id,output:JSON.stringify(r.result)})));
        url='https://api.openai.com/v1/responses';headers={Authorization:`Bearer ${settings.key}`};
        body={model:settings.model,input:native,tools:definitions,max_output_tokens:512,store:false,include:['reasoning.encrypted_content']};
      } else if(settings.provider==='anthropic') {
        if(results.length)native.push({role:'user',content:results.map(r=>({type:'tool_result',tool_use_id:r.id,content:JSON.stringify(r.result),is_error:object(r.result).isError===true}))});
        url='https://api.anthropic.com/v1/messages';headers={'x-api-key':settings.key,'anthropic-version':'2023-06-01'};
        body={model:settings.model,messages:native,tools:definitions,max_tokens:512};
      } else if(settings.provider==='gemini') {
        if(results.length)native.push({role:'user',parts:results.map(r=>({functionResponse:{id:r.id,name:r.name,response:{result:r.result}}}))});
        url=`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(settings.model)}:generateContent`;headers={'x-goog-api-key':settings.key};
        body={contents:native,tools:definitions,generationConfig:{maxOutputTokens:512}};
      } else {
        native.push(...results.map(r=>({role:'tool',tool_name:r.name,content:JSON.stringify(r.result)})));
        url=new URL('/api/chat',settings.ollamaHost).href;
        body={model:settings.model,messages:native,tools:definitions,stream:false,options:{num_predict:512}};
      }
      const response=await fetcher(url,{method:'POST',headers:{...headers,'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(60000),redirect:'error'});
      if(!response.ok || !response.body)throw new Error('Model unavailable');
      const reader=response.body.getReader();let text='';let bytes=0;const decoder=new TextDecoder();
      try {
        while(true){const part=await reader.read();if(part.done)break;bytes+=part.value.byteLength;if(bytes>256000)throw new Error('Model response too large');text+=decoder.decode(part.value,{stream:true});}
        text+=decoder.decode();
      }finally{await reader.cancel();reader.releaseLock();}
      const value=object(JSON.parse(text));
      if(settings.provider==='openai') {
        const output=objects(value.output);native.push(...output);
        return {text:output.filter(item=>item.type==='message').flatMap(item=>objects(item.content)).filter(part=>part.type==='output_text').map(part=>String(part.text)).join(''),calls:output.filter(item=>item.type==='function_call').map(item=>proposal(item.call_id,item.name,JSON.parse(string(item.arguments))))};
      }
      if(settings.provider==='anthropic') {
        const content=objects(value.content);native.push({role:'assistant',content});
        return {text:content.filter(item=>item.type==='text').map(item=>String(item.text)).join(''),calls:content.filter(item=>item.type==='tool_use').map(item=>proposal(item.id,item.name,item.input))};
      }
      if(settings.provider==='gemini') {
        const content=object(objects(value.candidates)[0].content);native.push(content);
        const parts=objects(content.parts);
        return {text:parts.filter(part=>part.text && !part.thought).map(part=>String(part.text)).join(''),calls:parts.filter(part=>part.functionCall).map(part=>{const call=object(part.functionCall);return proposal(call.id,call.name,call.args??{});})};
      }
      const message=object(value.message);native.push(message);
      return {text:String(message.content??''),calls:objects(message.tool_calls??[]).map((item,index)=>{const call=object(item.function);return proposal(`ollama-${turn}-${index}`,call.name,call.arguments);})};
    } catch {
      // Do not echo provider errors: they can contain tokens, URLs or private input.
      throw new Error(`Tool model request failed for ${settings.provider}. Run uv run python scripts/check_env.py.`);
    }
  };
}
