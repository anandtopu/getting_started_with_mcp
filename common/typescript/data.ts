import { readFileSync, realpathSync } from 'node:fs';
import { dirname, isAbsolute, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');

export function safePath(base: string, name: string): string {
  const canonicalBase = realpathSync(base);
  if (isAbsolute(name) || name.split(/[\\/]/).includes('..')) {
    throw new Error('Path must stay inside the allowed folder.');
  }
  const candidate = realpathSync(resolve(canonicalBase, name));
  const rel = relative(canonicalBase, candidate);
  if (rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)) {
    throw new Error('Path must stay inside the allowed folder.');
  }
  return candidate;
}

export function employees(): unknown[] {
  return JSON.parse(readFileSync(safePath(resolve(root, 'data'), 'directory/employees.json'), 'utf8'));
}
