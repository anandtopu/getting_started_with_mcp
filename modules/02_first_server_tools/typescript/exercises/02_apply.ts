/** Return an error tool result on denial and a text result after approval.
 * Run: npm exec tsx -- modules/02_first_server_tools/typescript/exercises/02_apply.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 2 2
 */
import { pathToFileURL } from 'node:url';
export function solve(confirmed: boolean) {
  void confirmed;
  // YOUR CODE HERE: Return an error tool result on denial and a text result after approval.
  return { content: [{ type: "text", text: "Saved" }], isError: false };
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, [false]));
}
