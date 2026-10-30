/** Run: npm exec tsx -- modules/10_streamable_http/typescript/examples/03_stream_recovery.ts */
import { withRemote, recoveryLab } from "../../../../common/typescript/remote_client.ts";
await withRemote(recoveryLab);
console.log("PASS recoveryLab");
