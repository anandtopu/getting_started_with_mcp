/** Current form retries: protocol-only stdout. */
import {serveStdio} from '@modelcontextprotocol/server/stdio';
import {advancedServer} from '../../../../common/typescript/advanced_server.ts';
serveStdio(advancedServer);
