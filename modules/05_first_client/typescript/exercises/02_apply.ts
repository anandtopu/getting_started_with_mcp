/** Distinguish protocol errors, tool failures, and successful responses.
 * Run: npm exec tsx -- modules/05_first_client/typescript/exercises/02_apply.ts
 * Check: npm exec tsx -- scripts/check-exercise.ts 5 2
 */
import { pathToFileURL } from 'node:url';
export function solve(message: { error?: unknown; result?: { isError?: boolean } }) {
  void message;
  // YOUR CODE HERE: Distinguish protocol errors, tool failures, and successful responses.
  return "error" in message ? "protocol" : "success";
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(Reflect.apply(solve, null, [{"error": {"code": -32601}}]));
}
