import { afterEach, expect, test, vi } from 'vitest';
import { designEvaluation } from './tool_design.ts';
import type { ModelSettings } from './llm.ts';

const settings:ModelSettings={provider:'ollama',model:'fixture',key:'',ollamaHost:'http://127.0.0.1:11434'};
afterEach(()=>vi.unstubAllEnvs());

test('offline evaluation uses real evidence through the host for all six cases',async()=>{
  const result=await designEvaluation();
  expect(result).toMatchObject({mode:'deterministic plumbing only',cases:6,budget:{turns:4,calls:4},
    mirror:{tools:25,completed:6,calls:6},task_tools:{tools:6,completed:6,calls:6}});
});

test('live route sends both catalogs to the provider and returns measured per-case evidence',async()=>{
  const sizes:number[]=[];
  const fetcher:typeof fetch=async(_url,init)=>{
    const body=JSON.parse(String(init?.body));
    sizes.push(body.tools.length);
    const last=body.messages.at(-1);
    if(last.role==='tool') {
      const {id,status}=JSON.parse(last.content).structuredContent;
      return Response.json({message:{content:JSON.stringify({id,status})}});
    }
    const id=Number(/Read issue (\d+)/.exec(last.content)![1]);
    const mirror=body.tools.length===25;
    return Response.json({message:{tool_calls:[{function:{name:mirror?'issues__get_issues':'issues__issue_brief',arguments:{[mirror?'row_id':'issue_id']:id}}}]}});
  };
  const result=await designEvaluation({live:true,limit:2,settings,fetcher});
  expect(sizes).toEqual([25,25,25,25,6,6,6,6]);
  expect(result).toMatchObject({mode:'live',cases:2,mirror:{completed:2,calls:2},task_tools:{completed:2,calls:2}});
  for(const label of ['mirror','task_tools']) {
    const score=result[label] as {seconds:number;results:unknown[]};
    expect(score.seconds).toBeGreaterThan(0);
    expect(score.results).toEqual([1,13].map(id=>({id,passed:true,error:false,calls:1,seconds:expect.any(Number)})));
  }
});

test.each(['invalid-json','provider-failure','budget','turn-budget','guessed-answer'])('live failures are recorded and bounded: %s',async mode=>{
  let requests=0;
  const fetcher:typeof fetch=async(_url,init)=>{
    requests++;
    if(mode==='provider-failure')throw new Error('private provider detail');
    const body=JSON.parse(String(init?.body));
    if(mode==='budget' || mode==='turn-budget')return Response.json({message:{tool_calls:Array.from({length:mode==='budget'?5:1},()=>({function:{
      name:body.tools.length===25?'issues__get_issues':'issues__issue_brief',
      arguments:{[body.tools.length===25?'row_id':'issue_id']:1},
    }}))}});
    return Response.json({message:{content:mode==='invalid-json'?'not JSON':'{"id":1,"status":"open"}'}});
  };
  const result=await designEvaluation({live:true,limit:1,settings,fetcher});
  expect(requests).toBe(mode==='turn-budget'?8:2);
  for(const label of ['mirror','task_tools'])expect(result[label]).toMatchObject({completed:0,calls:mode.endsWith('budget')?4:0,
    results:[{passed:false,error:mode!=='guessed-answer'}]});
  expect(JSON.stringify(result)).not.toContain('private provider detail');
});

test('limits and missing live configuration fail before making model requests',async()=>{
  for(const limit of [0,7,1.5,NaN])await expect(designEvaluation({limit})).rejects.toThrow('limit');
  vi.stubEnv('LLM_PROVIDER','fake');
  await expect(designEvaluation({live:true})).rejects.toThrow('Choose a live');
});
