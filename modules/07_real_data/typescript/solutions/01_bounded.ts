/** row_limit: Permit positive integer query limits through 20; reject all other input types. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return typeof value === "number" && Number.isInteger(value) && value >= 1 && value <= 20;
}
