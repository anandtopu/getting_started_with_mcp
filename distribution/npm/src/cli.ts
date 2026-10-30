import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { configuredNotesServer } from '../../../common/typescript/notes.ts';

const value = (process.env.LUMEN_NOTES_READ_ONLY ?? 'true').toLowerCase();
if (!['true', 'false'].includes(value)) throw new Error('LUMEN_NOTES_READ_ONLY must be true or false.');
serveStdio(() => configuredNotesServer(value === 'true'));
