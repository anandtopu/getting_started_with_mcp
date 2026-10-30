/** Choose text for text/* and blob for binary MIME types.
 * Run: npm exec tsx -- modules/03_resources/typescript/exercises/02_apply.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 3 2
 */
import { pathToFileURL } from 'node:url';
export function solve(mime: string) {
  void mime;
  // YOUR CODE HERE: Choose text for text/* and blob for binary MIME types.
  return "text";
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, ["text/markdown"]));
}
