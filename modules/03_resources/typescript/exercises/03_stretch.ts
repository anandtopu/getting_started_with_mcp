/** Invalidate only the updated URI; preserve unrelated cached values.
 * Run: npm exec tsx -- modules/03_resources/typescript/exercises/03_stretch.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 3 3
 */
import { pathToFileURL } from 'node:url';
export function solve(cache: Record<string, unknown>, changed_uri: string) {
  void cache;
  void changed_uri;
  // YOUR CODE HERE: Invalidate only the updated URI; preserve unrelated cached values.
  return { ...cache };
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, [{"wiki://index": "index", "lumen://bulletin": "old"}, "lumen://bulletin"]));
}
