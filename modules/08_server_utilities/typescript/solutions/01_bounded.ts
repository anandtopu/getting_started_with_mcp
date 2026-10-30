/** progress: Progress must be finite, nonnegative and no greater than a positive finite total. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return typeof value === "number" && typeof expected === "number" && Number.isFinite(value) && Number.isFinite(expected) && expected > 0 && value >= 0 && value <= expected;
}
