/** description: Require a trimmed nonempty tool description of at most 500 characters. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return typeof value === "string" && value.trim().length > 0 && value.length <= 500;
}
