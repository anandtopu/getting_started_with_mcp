/** Lumen workspace service. Run: npm exec tsx -- modules/02_first_server_tools/typescript/use_case/main.ts */
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { notesServer } from '../../../../common/typescript/notes.ts';
serveStdio(notesServer);
