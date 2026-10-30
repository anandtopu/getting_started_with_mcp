/** Keep source text in an embedded resource with its URI and MIME type.
 * Run: npm exec tsx -- modules/04_prompts/typescript/solutions/02_apply.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 4 2 --solution
 */
import { pathToFileURL } from 'node:url';
export function solve(uri: string, source: string) {

  return { role: "user", content: { type: "resource", resource: { uri, mimeType: "text/markdown", text: source } } };
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, ["wiki://engineering/page-01", "# Review"]));
}
