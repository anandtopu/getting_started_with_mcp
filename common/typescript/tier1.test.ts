import { describe, expect, test } from 'vitest';
import { inMemory, allResources } from './clients.ts';
import { notesServer } from './notes.ts';
import { wikiServer } from './wiki.ts';
import { promptServer } from './prompts.ts';
import { richServer } from './rich.ts';
import type { Client } from '@modelcontextprotocol/client';

describe('notes state and approvals', () => {
  test('denial leaves state unchanged; tags are idempotent; restart clears writes', async () => {
    await inMemory(notesServer, async client => {
      const args = { title: 'Review', body: 'Check wiki' };
      expect((await client.callTool({ name: 'create_note', arguments: args })).isError).toBe(true);
      const created = await client.callTool({ name: 'create_note', arguments: { ...args, confirmed: true } });
      expect(created.structuredContent).toEqual({ id: 2, title: 'Review' });
      for (let i = 0; i < 2; i++) {
        const tagged = await client.callTool({ name: 'tag_note', arguments: { note_id: 2, tag: 'ship', confirmed: true } });
        expect(tagged.structuredContent).toEqual({ id: 2, tags: ['ship'] });
      }
      expect((await client.callTool({ name: 'create_note', arguments: { title: '', body: 'x', confirmed: true } })).isError).toBe(true);
    });
    await inMemory(notesServer, async client => {
      const result = await client.callTool({ name: 'search_notes', arguments: {} });
      expect((result.structuredContent as { result: unknown[] }).result).toHaveLength(1);
    });
  });
});

test('rich result shapes and failed output contract', async () => {
  await inMemory(richServer, async client => {
    expect((await client.callTool({ name: 'release_summary', arguments: {} })).structuredContent).toEqual({ title: 'Lumen release review', open_issues: 3 });
    expect((await client.callTool({ name: 'release_summary', arguments: { open_issues: -1 } })).isError).toBe(true);
    const result = await client.callTool({ name: 'review_assets', arguments: {} });
    expect(result.content.map(c => c.type)).toEqual(['image', 'audio', 'resource', 'resource_link']);
  });
});

test('wiki rejects traversal and returns valid PDF bytes', async () => {
  await inMemory(wikiServer, async client => {
    const pdf = (await client.readResource({ uri: 'lumen://contract/1' })).contents[0];
    expect('blob' in pdf && Buffer.from(String(pdf.blob), 'base64').subarray(0, 4).toString()).toBe('%PDF');
    await expect(client.readResource({ uri: 'wiki://engineering/../secret' })).rejects.toThrow();
  });
});

test('subscription routes only requested resource changes', async () => {
  await inMemory(wikiServer, async client => {
    const events: string[] = [];
    client.setNotificationHandler('notifications/resources/updated', n => { events.push(n.params.uri); });
    const sub = await client.listen({ resourceSubscriptions: ['lumen://bulletin'] });
    try {
      expect(sub.honoredFilter.resourceSubscriptions).toEqual(['lumen://bulletin']);
      await client.callTool({ name: 'update_bulletin', arguments: { text: 'Checked', confirmed: true } });
      await expect.poll(() => events).toEqual(['lumen://bulletin']);
      expect((await client.readResource({ uri: 'lumen://bulletin' })).contents[0]).toMatchObject({ text: 'Checked' });
    } finally { await sub.close(); }
  });
});

test('prompt embeds a source and completion uses prior arguments', async () => {
  await inMemory(promptServer, async client => {
    const result = await client.getPrompt({ name: 'summarize_incident', arguments: {} });
    expect(result.messages.map(m => m.content.type)).toEqual(['text', 'resource']);
    const params = { ref: { type: 'ref/prompt' as const, name: 'summarize_incident' }, argument: { name: 'page', value: 'page-01' } };
    expect((await client.complete(params)).completion.values).toEqual([]);
    expect((await client.complete({ ...params, context: { arguments: { space: 'engineering' } } })).completion.values).toEqual(['page-01']);
    await expect(client.getPrompt({ name: 'prepare_meeting', arguments: { customer_id: '999' } })).rejects.toThrow();
  });
});

test('pagination stops repeated cursors and honors an empty page', async () => {
  let step = 0;
  const pages = [{ resources: [], nextCursor: 'next' }, { resources: [{ uri: 'wiki://index', name: 'Index' }] }];
  const client = { listResources: async () => pages[step++] } as unknown as Client;
  expect(await allResources(client)).toHaveLength(1);
  const repeat = { listResources: async () => ({ resources: [], nextCursor: 'repeat' }) } as unknown as Client;
  await expect(allResources(repeat)).rejects.toThrow('Repeated cursor');
  await expect(allResources(repeat, 1)).rejects.toThrow('budget');
});
