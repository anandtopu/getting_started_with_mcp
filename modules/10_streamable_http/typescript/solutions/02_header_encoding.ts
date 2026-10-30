/** Encode Unicode, edge whitespace, controls, and sentinel-shaped text as UTF-8 base64.
 * Run: npm exec tsx -- scripts/check-exercise.ts 10 2 --solution
 */
export function solve(value: string): unknown {
  const safe = value === value.trim() && [...value].every(c => c.charCodeAt(0) >= 32 && c.charCodeAt(0) <= 126);
  const sentinel = value.startsWith('=?base64?') && value.endsWith('?=');
  return safe && !sentinel ? value : '=?base64?' + Buffer.from(value, 'utf8').toString('base64') + '?=';
}
