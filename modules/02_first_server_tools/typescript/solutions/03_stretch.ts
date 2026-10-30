/** Add a tag idempotently while preserving insertion order and the original list.
 * Run: npm exec tsx -- modules/02_first_server_tools/typescript/solutions/03_stretch.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 2 3 --solution
 */
import { pathToFileURL } from 'node:url';
export function solve(tags: string[], tag: string) {

  return tags.includes(tag) ? [...tags] : [...tags, tag];
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, [["release"], "release"]));
}
