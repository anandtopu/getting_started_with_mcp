/** loopback: Permit exactly 127.0.0.1 or localhost for the default bind; reject public and lookalike names. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return value === "127.0.0.1" || value === "localhost";
}
