import { McpServer, type ToolAnnotations } from '@modelcontextprotocol/server';
import { z } from 'zod';

export const read: ToolAnnotations = {
  readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false,
};
export const write: ToolAnnotations = { ...read, readOnlyHint: false, idempotentHint: false };
export const text = (value: string) => ({ content: [{ type: 'text' as const, text: value }] });
export const failure = (message: string) => ({ ...text(message), isError: true });
export const structured = (value: Record<string, unknown>) => ({
  ...text(JSON.stringify(value)), structuredContent: value,
});

export function configuredNotesServer(readOnly = false): McpServer {
  const server = new McpServer({ name: 'Lumen notes', version: '1.0' });
  const notes = [{ id: 1, title: 'Release handover', body: 'Review the release checklist.', tags: ['release'] }];
  server.registerTool('search_notes', {
    description: 'Find notes whose title or body contains query, ignoring case. Empty query lists all.',
    inputSchema: z.object({ query: z.string().max(100).default('') }), annotations: read,
    outputSchema: z.object({ result: z.array(z.object({ id: z.number(), title: z.string(), body: z.string(), tags: z.array(z.string()) })) }),
  }, ({ query }) => structured({ result: notes.filter(n => `${n.title} ${n.body}`.toLowerCase().includes(query.toLowerCase())) }));
  const create = server.registerTool('create_note', {
    description: 'Create an ephemeral note only after the user confirms. Restarting clears new notes.',
    inputSchema: z.object({ title: z.string().min(1).max(100), body: z.string().min(1).max(2000), confirmed: z.boolean().default(false) }),
    outputSchema: z.object({ id: z.number(), title: z.string() }), annotations: write,
  }, ({ title, body, confirmed }) => {
    if (!confirmed) return failure('Confirmation required: review the title and body before creating.');
    const note = { id: notes.length + 1, title, body, tags: [] as string[] };
    notes.push(note);
    return structured({ id: note.id, title });
  });
  const tag = server.registerTool('tag_note', {
    description: 'Add a tag once to an existing note. Confirm the note ID and tag first.',
    inputSchema: z.object({ note_id: z.number().int(), tag: z.string().min(1).max(40), confirmed: z.boolean().default(false) }),
    outputSchema: z.object({ id: z.number(), tags: z.array(z.string()) }),
    annotations: { ...write, idempotentHint: true },
  }, ({ note_id, tag, confirmed }) => {
    if (!confirmed) return failure('Confirmation required: review the note ID and tag.');
    const note = notes.find(n => n.id === note_id);
    if (!note) return failure('Note not found: search notes to obtain a valid ID.');
    if (!note.tags.includes(tag)) note.tags.push(tag);
    return structured({ id: note_id, tags: note.tags });
  });
  if (readOnly) { create.remove(); tag.remove(); }
  return server;
}

export function notesServer(): McpServer { return configuredNotesServer(false); }
