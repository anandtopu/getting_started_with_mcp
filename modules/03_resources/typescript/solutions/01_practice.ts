/** Validate known wiki segments before assembling a URI; return None for unknown pages.
 * Run: npm exec tsx -- modules/03_resources/typescript/solutions/01_practice.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 3 1 --solution
 */
import { pathToFileURL } from 'node:url';
export function solve(space: string, page: string) {

  return ["engineering","product","hr","onboarding","incident_postmortems"].includes(space) && /^page-0[1-8]$/.test(page) ? `wiki://${space}/${page}` : null;
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, ["engineering", "page-01"]));
}
