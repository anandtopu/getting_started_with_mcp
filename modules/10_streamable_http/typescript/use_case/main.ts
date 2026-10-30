/** Run: npm exec tsx -- modules/10_streamable_http/typescript/use_case/main.ts */
import { withRemote, headerLab, recoveryLab } from "../../../../common/typescript/remote_client.ts";
await withRemote(async url => { await headerLab(url); await recoveryLab(url); });
console.log("PASS remote workspace");
