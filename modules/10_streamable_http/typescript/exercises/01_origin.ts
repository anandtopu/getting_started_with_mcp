/** Accept absent Origin or exactly the configured browser origin.
 * Run: npm exec tsx -- scripts/check-exercise.ts 10 1
 */
export function solve(origin: string | null): unknown {
  // YOUR CODE HERE: Accept absent Origin or exactly the configured browser origin.
  return origin === "http://localhost:3000";
}
