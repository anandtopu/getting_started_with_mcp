/** Offer page completions only when prior context names a valid space.
 * Run: npm exec tsx -- modules/04_prompts/typescript/solutions/03_stretch.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 4 3 --solution
 */
import { pathToFileURL } from 'node:url';
export function solve(prefix: string, context: Record<string, string>) {

  return ["engineering","product","hr","onboarding","incident_postmortems"].includes(context.space) ? Array.from({ length: 8 }, (_, i) => `page-0${i + 1}`).filter(p => p.startsWith(prefix)) : [];
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, ["page-01", {"space": "engineering"}]));
}
