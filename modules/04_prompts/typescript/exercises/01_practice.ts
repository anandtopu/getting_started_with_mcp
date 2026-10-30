/** Filter wiki spaces by a case-sensitive prefix.
 * Run: npm exec tsx -- modules/04_prompts/typescript/exercises/01_practice.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 4 1
 */
import { pathToFileURL } from 'node:url';
export function solve(prefix: string) {
  void prefix;
  // YOUR CODE HERE: Filter wiki spaces by a case-sensitive prefix.
  return ["engineering","product","hr","onboarding","incident_postmortems"];
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, ["eng"]));
}
