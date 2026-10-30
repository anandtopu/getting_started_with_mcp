/** bundle_version: Accept the taught MCPB manifest version 0.3 as a string only. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return value === "0.3";
}
