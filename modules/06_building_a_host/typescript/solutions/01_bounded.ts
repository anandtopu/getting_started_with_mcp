/** tool_namespace: Accept exactly two safe server/tool names joined by a double underscore. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return typeof value === "string" && /^[a-z][a-z0-9_]*__[a-z][a-z0-9_]*$/.test(value);
}
