/** Make the name field required and reject empty names in a tool input schema.
 * Run: npm exec tsx -- modules/02_first_server_tools/typescript/exercises/01_practice.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 2 1
 */
import { pathToFileURL } from 'node:url';
export function solve() {

  // YOUR CODE HERE: Make the name field required and reject empty names in a tool input schema.
  return { type: "object", properties: { name: { type: "string" } } };
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, []));
}
