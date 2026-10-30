/** Validate known wiki segments before assembling a URI; return None for unknown pages.
 * Run: npm exec tsx -- modules/03_resources/typescript/exercises/01_practice.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 3 1
 */
import { pathToFileURL } from 'node:url';
export function solve(space: string, page: string) {
  void space;
  void page;
  // YOUR CODE HERE: Validate known wiki segments before assembling a URI; return None for unknown pages.
  return `wiki://${space}/${page}`;
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, ["engineering", "page-01"]));
}
