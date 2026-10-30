/** registry_name: Require the exact io.github.anandtopu namespace followed by a lowercase package slug. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return typeof value === "string" && /^io\.github\.anandtopu\/[a-z][a-z0-9-]*$/.test(value);
}
