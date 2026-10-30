/** Return an error tool result on denial and a text result after approval.
 * Run: npm exec tsx -- modules/02_first_server_tools/typescript/solutions/02_apply.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 2 2 --solution
 */
import { pathToFileURL } from 'node:url';
export function solve(confirmed: boolean) {

  return { content: [{ type: "text", text: confirmed ? "Saved" : "Confirmation required" }], isError: !confirmed };
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, [false]));
}
