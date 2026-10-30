/** response_id: A response matches only an exact string/number request ID; reject null IDs. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return value !== null && (typeof value === "string" || typeof value === "number") && value === expected;
}
