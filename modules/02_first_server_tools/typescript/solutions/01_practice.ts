/** Make the name field required and reject empty names in a tool input schema.
 * Run: npm exec tsx -- modules/02_first_server_tools/typescript/solutions/01_practice.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 2 1 --solution
 */
import { pathToFileURL } from 'node:url';
export function solve() {

  return { type: "object", properties: { name: { type: "string", minLength: 1 } }, required: ["name"] };
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, []));
}
