/** Protocol-only stdio server for Skills interop captures. */
import {serveStdio} from '@modelcontextprotocol/server/stdio';
import {skillsFactory} from '../../../../common/typescript/skills.ts';
serveStdio(await skillsFactory());
