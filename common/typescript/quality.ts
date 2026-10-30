/** Explicit OTel spans around actual MCP calls, bounded HTTP load and fixture evals. */
import { strict as assert } from 'node:assert';
import { performance } from 'node:perf_hooks';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { ROOT_CONTEXT, SpanStatusCode, trace } from '@opentelemetry/api';
import { TracerProvider, SimpleSpanProcessor, InMemorySpanExporter } from '@opentelemetry/sdk-trace';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/client';
import { inMemory, newClient } from './clients.ts';
import { notesServer } from './notes.ts';
import { withRemote } from './remote_client.ts';
import { root } from './data.ts';

export function validateStdout(text:string) {
  const lines=text.trim().split('\n');
  for(const line of lines) {
    try {const value=JSON.parse(line);if(value.jsonrpc!=='2.0')throw new Error('envelope');}
    catch {throw new Error('Protocol stdout corrupted: send diagnostics to stderr.');}
  }
  return lines.length;
}

export async function traces() {
  const exporter=new InMemorySpanExporter();
  const provider=new TracerProvider({spanProcessors:[new SimpleSpanProcessor({exporter})]});
  const tracer=provider.getTracer('lumen.typescript');
  const parent=tracer.startSpan('quality-run');
  const context=trace.setSpan(ROOT_CONTEXT,parent);
  try {
    await inMemory(notesServer,async client=>{
      for(const [name,args] of [['search_notes',{}],['create_note',{title:'',body:'private fixture'}]] as const) {
        // KEY IDEA: export method/status, never arguments, results or credentials.
        const span=tracer.startSpan('tools/call',{attributes:{'mcp.method.name':'tools/call'}},context);
        try {const result=await client.callTool({name,arguments:args});span.setStatus({code:result.isError?SpanStatusCode.ERROR:SpanStatusCode.OK});}
        catch {span.setStatus({code:SpanStatusCode.ERROR});throw new Error('Contract call failed');}
        finally {span.end();}
      }
    });
    parent.end();await provider.forceFlush();
    const spans=exporter.getFinishedSpans();
    const children=spans.filter(span=>span.name==='tools/call');
    assert.equal(children.length,2);
    assert.ok(children.every(span=>span.spanContext().traceId===parent.spanContext().traceId));
    assert.ok(children.some(span=>span.status.code===SpanStatusCode.ERROR));
    return spans.map(span=>({name:span.name,traceId:span.spanContext().traceId,status:span.status.code,attributes:span.attributes}));
  }finally{parent.end();await provider.shutdown();}
}

export async function load() {
  const durations:number[]=[];const started=performance.now();
  await withRemote(async url=>{
    await Promise.all([0,1].map(async()=>{
      const client=newClient();
      try {
        await client.connect(new StreamableHTTPClientTransport(url));await client.discover();
        for(let request=0;request<5;request++) {
          const begin=performance.now();
          assert.equal((await client.callTool({name:'read_issue',arguments:{issue_id:1}},{timeout:3000})).isError===true,false);
          durations.push(performance.now()-begin);
        }
      }finally{await client.close();}
    }));
  });
  durations.sort((a,b)=>a-b);
  return {requests:durations.length,concurrency:2,p95_ms:durations[Math.ceil(durations.length*.95)-1],elapsed_ms:performance.now()-started};
}

export function evaluate() {
  const rows=readFileSync(resolve(root,'data/eval/tool_selection.jsonl'),'utf8').trim().split('\n').map(line=>JSON.parse(line));
  let correct=0;
  for(const row of rows) {
    const match=/^Read Lumen issue ([1-9][0-9]*)$/.exec(row.request);
    const calls=match?[{name:'issues_get',arguments:{issue_id:Number(match[1])}}]:[];
    if(JSON.stringify(calls)===JSON.stringify(row.expected_calls))correct++;
  }
  return {mode:'deterministic selector; not live model accuracy',correct,total:rows.length};
}
