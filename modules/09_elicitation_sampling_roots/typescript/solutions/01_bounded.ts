/** input_decision: A form answer permits publication only for accept plus an explicit true approval. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return value === "accept" && expected === true;
}
