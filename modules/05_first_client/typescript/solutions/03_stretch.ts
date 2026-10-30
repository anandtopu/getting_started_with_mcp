/** Clear only the resource catalog on its list-change event.
 * Run: npm exec tsx -- modules/05_first_client/typescript/solutions/03_stretch.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 5 3 --solution
 */
import { pathToFileURL } from 'node:url';
export function solve(cache: Record<string, unknown>, method: string) {

  return Object.fromEntries(Object.entries(cache).filter(([key]) => key !== "resources" || method !== "notifications/resources/list_changed"));
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, [{"resources": ["old"], "tools": ["search"]}, "notifications/resources/list_changed"]));
}
