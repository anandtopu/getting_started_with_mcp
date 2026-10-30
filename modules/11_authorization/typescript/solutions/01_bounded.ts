/** audience: Require an exact nonempty expected audience; prefixes and arrays do not qualify. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return typeof value === "string" && typeof expected === "string" && expected.length > 0 && value === expected;
}
