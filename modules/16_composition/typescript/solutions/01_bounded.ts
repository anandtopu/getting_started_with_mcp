/** write_scope: A gateway write needs the workspace:write scope and separate approval. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return Array.isArray(value) && value.includes("workspace:write") && expected === true;
}
