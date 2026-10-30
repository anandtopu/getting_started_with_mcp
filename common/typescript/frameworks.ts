/** Three actual JS runtimes call the same read-only MCP workflow without a model key. */
import { Agent, Runner, tool, Usage, type Model, type ModelResponse } from '@openai/agents';
import { RunnableLambda, RunnableSequence } from '@langchain/core/runnables';
import { Annotation, StateGraph, START, END } from '@langchain/langgraph';
import { z } from 'zod';
import { inMemory } from './clients.ts';

import { workflowServer } from './workflow.ts';
export async function frameworkDemo(kind:'agents'|'langchain'|'langgraph') {
  return inMemory(workflowServer,async client=>{
    const calls:string[]=[];
    const invoke=async(name:string)=>{calls.push(name);return JSON.stringify((await client.callTool({name,arguments:{week_start:'2026-07-13'}})).structuredContent);};
    let draft='';
    if(kind==='agents') {
      let step=0;
      const model:Model={
        async getResponse():Promise<ModelResponse> {
          step++;
          return {usage:new Usage(),output:step<=2?[{type:'function_call',callId:`call-${step}`,name:step===1?'triage_week':'draft_status',arguments:'{"week_start":"2026-07-13"}'}]:[{type:'message',role:'assistant',status:'completed',content:[{type:'output_text',text:draft}]}]};
        },
        // eslint-disable-next-line require-yield -- streaming is deliberately unsupported in the fixture
        async *getStreamedResponse(){throw new Error('Use the non-streaming teaching runner');},
      };
      const tools=['triage_week','draft_status'].map(name=>tool({name,description:'Read synthetic evidence; do not publish.',parameters:z.object({week_start:z.literal('2026-07-13')}),execute:async()=>{const value=await invoke(name);if(name==='draft_status')draft=value;return value;}}));
      const agent=new Agent({name:'Lumen triage',model,tools});
      const result=await new Runner({tracingDisabled:true}).run(agent,'Triage this week and draft a status update.',{maxTurns:4});
      draft=String(result.finalOutput);
    } else if(kind==='langchain') {
      const chain=RunnableSequence.from([RunnableLambda.from(async()=>invoke('triage_week')),RunnableLambda.from(async evidence=>{if(!evidence)throw new Error('Missing triage evidence');return invoke('draft_status');})]);
      draft=await chain.invoke({});
    } else {
      const State=Annotation.Root({evidence:Annotation<string>(),draft:Annotation<string>()});
      const graph=new StateGraph(State).addNode('triage',async()=>({evidence:await invoke('triage_week')})).addNode('drafting',async state=>{if(!state.evidence)throw new Error('Missing triage evidence');return {draft:await invoke('draft_status')};}).addEdge(START,'triage').addEdge('triage','drafting').addEdge('drafting',END).compile();
      draft=(await graph.invoke({evidence:'',draft:''})).draft;
    }
    if(calls.join(',')!=='triage_week,draft_status' || !draft.includes('synthetic issues')) throw new Error('Framework skipped evidence');
    return {framework:kind,calls,draft};
  });
}
