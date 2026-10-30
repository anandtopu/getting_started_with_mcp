/** tool_outcome: An evaluation succeeds only when a complete result is not an application error. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return value === "complete" && expected === false;
}
