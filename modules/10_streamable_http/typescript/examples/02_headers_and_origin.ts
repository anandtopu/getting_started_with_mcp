/** Run: npm exec tsx -- modules/10_streamable_http/typescript/examples/02_headers_and_origin.ts */
import { withRemote, headerLab } from "../../../../common/typescript/remote_client.ts";
await withRemote(headerLab);
console.log("PASS headerLab");
