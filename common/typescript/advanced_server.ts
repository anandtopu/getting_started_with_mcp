/** Native TypeScript form retries, bounded reports and approval-bound notes. */
import { McpServer, inputRequired, acceptedContent } from '@modelcontextprotocol/server';
import { z } from 'zod';
import { setTimeout as pause } from 'node:timers/promises';
import { read, write, structured, failure } from './notes.ts';
import { ReviewLedger } from './advanced_policy.ts';

export function advancedServer() {
  const server = new McpServer({ name:'Lumen TypeScript workflow', version:'1.0' });
  const ledger = new ReviewLedger();
  let bulletin = 'Release review pending';
  const confirmation = z.object({ approve:z.boolean() });
  server.registerTool('read_bulletin', { description:'Read the synthetic review bulletin.', inputSchema:z.object({}), annotations:read }, () => structured({text:bulletin}));
  server.registerTool('review_bulletin', {
    description:'Ask the user to approve exact bulletin text before replacing the ephemeral bulletin.',
    inputSchema:z.object({text:z.string().min(1).max(200)}), annotations:write,
  }, ({text},ctx) => {
    const state=ctx.mcpReq.requestState<string>();
    if(!state) return inputRequired({requestState:ledger.issue(text),inputRequests:{decision:inputRequired.elicit({message:`Publish this exact bulletin: ${text}?`,requestedSchema:confirmation})}});
    ledger.take(state,text);
    const answer=acceptedContent(ctx.mcpReq.inputResponses,'decision',confirmation);
    if(answer?.approve!==true) return structured({published:false});
    bulletin=text;return structured({published:true});
  });
  server.registerTool('quarterly_report', {
    description:'Generate a cancellable synthetic report; dates are simulated.',
    inputSchema:z.object({quarter:z.enum(['Q1','Q2','Q3','Q4']).default('Q1')}),annotations:read,
  }, async ({quarter},ctx) => {
    for(let progress=1;progress<=4;progress++) {
      await pause(10,undefined,{signal:ctx.mcpReq.signal});
      const token=ctx.mcpReq._meta?.progressToken;
      if(token!==undefined) await ctx.mcpReq.notify({method:'notifications/progress',params:{progressToken:token,progress,total:4}});
    }
    return structured({quarter,total:400,scope:'all fixture issues'});
  });
  server.registerTool('checked_note', {description:'Check a synthetic note length without writing it.',inputSchema:z.object({text:z.string()}),annotations:read}, ({text}) => text.length>200 ? failure('Note exceeds 200 characters') : structured({length:text.length}));
  return server;
}
