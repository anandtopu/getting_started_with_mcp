/** supported_node: Accept integer Node major 24 or 26; reject unsupported versions. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return Number.isInteger(value) && [24,26].includes(Number(value));
}
