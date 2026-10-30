/** Lumen workspace service. Run: npm exec tsx -- modules/03_resources/typescript/use_case/main.ts */
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { wikiServer } from '../../../../common/typescript/wiki.ts';
serveStdio(wikiServer);
