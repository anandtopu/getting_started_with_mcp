/** Filter wiki spaces by a case-sensitive prefix.
 * Run: npm exec tsx -- modules/04_prompts/typescript/solutions/01_practice.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 4 1 --solution
 */
import { pathToFileURL } from 'node:url';
export function solve(prefix: string) {

  return ["engineering","product","hr","onboarding","incident_postmortems"].filter(space => space.startsWith(prefix));
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, ["eng"]));
}
