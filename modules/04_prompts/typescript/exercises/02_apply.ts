/** Keep source text in an embedded resource with its URI and MIME type.
 * Run: npm exec tsx -- modules/04_prompts/typescript/exercises/02_apply.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 4 2
 */
import { pathToFileURL } from 'node:url';
export function solve(uri: string, source: string) {
  void uri;
  void source;
  // YOUR CODE HERE: Keep source text in an embedded resource with its URI and MIME type.
  return { role: "user", content: { type: "text", text: source } };
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, ["wiki://engineering/page-01", "# Review"]));
}
