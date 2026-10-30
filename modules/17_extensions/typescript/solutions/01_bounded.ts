/** terminal_task: Recognize completed, failed and cancelled as terminal; input_required and working are not. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return typeof value === "string" && ["completed","failed","cancelled"].includes(value);
}
