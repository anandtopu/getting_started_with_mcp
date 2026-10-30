/** Invalidate only the updated URI; preserve unrelated cached values.
 * Run: npm exec tsx -- modules/03_resources/typescript/solutions/03_stretch.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 3 3 --solution
 */
import { pathToFileURL } from 'node:url';
export function solve(cache: Record<string, unknown>, changed_uri: string) {

  return Object.fromEntries(Object.entries(cache).filter(([uri]) => uri !== changed_uri));
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, [{"wiki://index": "index", "lumen://bulletin": "old"}, "lumen://bulletin"]));
}
