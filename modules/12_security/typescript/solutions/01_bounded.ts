/** secret_key: Identify these credential field names case-insensitively: authorization, access_token, client_secret, assertion. */
export function solve(value: unknown, expected?: unknown): boolean {
  void expected;
  return typeof value === "string" && ["authorization","access_token","client_secret","assertion"].includes(value.toLowerCase());
}
