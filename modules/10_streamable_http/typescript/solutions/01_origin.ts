/** Accept absent Origin or exactly the configured browser origin.
 * Run: npm exec tsx -- scripts/check-exercise.ts 10 1 --solution
 */
export function solve(origin: string | null): unknown {
  return origin === null || origin === "http://localhost:3000";
}
