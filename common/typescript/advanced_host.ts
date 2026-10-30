/** A bounded provider-neutral host: model proposals never authorize themselves. */
import { createHash } from 'node:crypto';
import type { Client, Tool, CallToolResult } from '@modelcontextprotocol/client';

export type Proposal = { name: string; arguments: Record<string, unknown> };
export type Model = (messages: readonly unknown[], tools: readonly Tool[]) => Promise<{ text?: string; calls?: Proposal[] }>;
export type Approve = (call: Proposal, tool: Tool) => Promise<boolean>;

function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([k,v]) => `${JSON.stringify(k)}:${canonical(v)}`).join(',')}}`;
  return JSON.stringify(value) ?? 'null';
}
export const fingerprint = (tool: Tool) => createHash('sha256').update(canonical(tool)).digest('hex');

export class CourseHost {
  constructor(readonly clients: Map<string, Client>, readonly approve: Approve) {}
  async catalog() {
    const tools: Tool[] = [];
    for (const [alias, client] of this.clients) {
      if (!/^[a-z][a-z0-9_]{0,15}$/.test(alias)) throw new Error('Unsafe server alias');
      let cursor: string | undefined;
      const seen = new Set<string>();
      for (let page = 0; page < 20; page++) {
        const result = await client.listTools({ cursor });
        for (const tool of result.tools) tools.push({ ...tool, name: `${alias}__${tool.name}` });
        cursor = result.nextCursor;
        if (!cursor) break;
        if (seen.has(cursor) || page === 19) throw new Error('Catalog page budget exceeded');
        seen.add(cursor);
      }
    }
    if (new Set(tools.map(t => t.name)).size !== tools.length) throw new Error('Duplicate tool names');
    return tools;
  }
  async execute(call: Proposal): Promise<CallToolResult> {
    const tool = (await this.catalog()).find(t => t.name === call.name);
    if (!tool) throw new Error('Unknown tool');
    const reviewed = structuredClone(call);
    const signature = fingerprint(tool);
    if (!await this.approve(structuredClone(reviewed), structuredClone(tool))) throw new Error('User declined');
    const current = (await this.catalog()).find(t => t.name === reviewed.name);
    if (!current || fingerprint(current) !== signature) throw new Error('Tool changed; review again');
    const [alias, ...rest] = reviewed.name.split('__');
    const args = { ...reviewed.arguments };
    // This bit is supplied only after the separate host decision, never from a model's claim.
    if ('confirmed' in (tool.inputSchema.properties ?? {})) args.confirmed = true;
    const result = await this.clients.get(alias)!.callTool({ name: rest.join('__'), arguments: args });
    return result as CallToolResult;
  }
  async run(model: Model, request: string) {
    const history: unknown[] = [{ role: 'user', content: request }];
    let calls = 0;
    for (let turn = 0; turn < 6; turn++) {
      const reply = await model(history, await this.catalog());
      if (!reply.calls?.length) return { text: reply.text ?? '', calls };
      history.push(reply);
      for (const proposal of reply.calls) {
        if (++calls > 8) throw new Error('Tool call budget exceeded');
        history.push({ role: 'tool', name: proposal.name, result: await this.execute(proposal) });
      }
    }
    throw new Error('Model turn budget exceeded');
  }
}

export function fakeModel(call: Proposal): Model {
  let used = false;
  return async () => {
    if (used) return { text: 'Reviewed synthetic evidence.' };
    used = true; return { calls: [call] };
  };
}

export function providerTools(tools: Tool[], provider: 'openai'|'anthropic'|'gemini'|'ollama') {
  // Each branch produces the provider's advertised function-description shape.
  return tools.map(t => provider === 'anthropic'
    ? { name: t.name, description: t.description, input_schema: t.inputSchema }
    : provider === 'gemini'
      ? { name: t.name, description: t.description, parametersJsonSchema: t.inputSchema }
      : provider === 'openai'
        ? { type: 'function', name: t.name, description: t.description, parameters: t.inputSchema }
        : { type: 'function', function: { name: t.name, description: t.description, parameters: t.inputSchema } });
}
