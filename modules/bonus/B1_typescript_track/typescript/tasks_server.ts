/** Current Tasks extension over official framing; read module 17's SDK limitation. */
import {StdioServerTransport} from '@modelcontextprotocol/server/stdio';
import {Tasks} from '../../../../common/typescript/task_receiver.ts';
import {serveRaw} from '../../../../common/typescript/protocol_peer.ts';
const tasks=new Tasks();const transport=new StdioServerTransport();transport.onclose=()=>tasks.close();
await serveRaw(transport,(method,params,caps)=>tasks.dispatch(method,params,caps));
