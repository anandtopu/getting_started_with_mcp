/** Continue pagination by nextCursor even if the current page is empty.
 * Run: npm exec tsx -- modules/05_first_client/typescript/exercises/01_practice.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 5 1
 */
import { pathToFileURL } from 'node:url';
export function solve(page: { resources?: unknown[]; nextCursor?: string }) {
  void page;
  // YOUR CODE HERE: Continue pagination by nextCursor even if the current page is empty.
  return page.resources?.length ? page.nextCursor ?? null : null;
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, [{"resources": [], "nextCursor": "next"}]));
}
