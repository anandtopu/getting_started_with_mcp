/** Retry a read, or a write with a server-enforced operation key; a lost response proves no outcome.
 * Run: npm exec tsx -- scripts/check-exercise.ts 10 3
 */
export function solve(operation: string, has_key: boolean): unknown {
  // YOUR CODE HERE: Retry a read, or a write with a server-enforced operation key; a lost response proves no outcome.
  return operation === "read" && !has_key;
}
