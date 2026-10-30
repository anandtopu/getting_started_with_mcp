/** Choose text for text/* and blob for binary MIME types.
 * Run: npm exec tsx -- modules/03_resources/typescript/solutions/02_apply.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 3 2 --solution
 */
import { pathToFileURL } from 'node:url';
export function solve(mime: string) {

  return mime.startsWith("text/") ? "text" : "blob";
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, ["text/markdown"]));
}
