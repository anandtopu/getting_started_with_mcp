/** retry_read: Permit one retry only for the local read allowlist, never for writes or a second retry. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return typeof value === "string" && ["search_notes","triage_week","draft_status"].includes(value) && expected === 0;
}
