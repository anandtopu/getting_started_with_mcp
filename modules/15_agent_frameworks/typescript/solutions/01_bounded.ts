/** tool_history: A returned framework tool result must match the outstanding nonempty call ID exactly. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return typeof value === "string" && value.length > 0 && value === expected;
}
