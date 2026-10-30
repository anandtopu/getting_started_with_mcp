/** Retry a read, or a write with a server-enforced operation key; a lost response proves no outcome.
 * Run: npm exec tsx -- scripts/check-exercise.ts 10 3 --solution
 */
export function solve(operation: string, has_key: boolean): unknown {
  return operation === "read" || (operation === "write" && has_key);
}
