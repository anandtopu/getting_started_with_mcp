/** Lumen workspace service. Run: npm exec tsx -- modules/04_prompts/typescript/use_case/main.ts */
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { promptServer } from '../../../../common/typescript/prompts.ts';
serveStdio(promptServer);
