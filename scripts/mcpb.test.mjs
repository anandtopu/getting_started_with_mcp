import { afterEach, beforeEach, expect, test } from 'vitest';
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync, symlinkSync, truncateSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, URL } from 'node:url';
import { unzipSync, strFromU8 } from 'fflate';
import { limits, pack, validateManifest } from './mcpb.mjs';

let root, stage, manifest, output;
const notes = JSON.parse(readFileSync(new URL('../distribution/mcpb/manifest.json', import.meta.url), 'utf8'));
beforeEach(() => {
  root = mkdtempSync(join(tmpdir(), 'mcpb-test-'));
  stage = join(root, 'bundle');
  mkdirSync(join(stage, 'server'), { recursive: true });
  manifest = join(stage, 'manifest.json');
  writeFileSync(manifest, JSON.stringify(notes));
  writeFileSync(join(stage, 'server/cli.cjs'), 'console.log("bundle launched")');
  output = join(root, 'notes.mcpb');
});
afterEach(() => rmSync(root, { recursive: true, force: true }));

test('official pinned schema is unchanged and both course manifests validate', () => {
  const schema = readFileSync(new URL('../distribution/mcpb/schema/manifest-v0.3.schema.json', import.meta.url));
  expect(createHash('sha256').update(schema).digest('hex')).toBe('3a0ac9d845711a1b9b17dfa5a52f8b60628239d6a86a9db417206a9efc78592d');
  expect(validateManifest(manifest).name).toBe(notes.name);
  expect(validateManifest(new URL('../capstones/01_personal_knowledge/package/mcpb.json', import.meta.url)).server.type).toBe('python');
});

test('pack produces a deterministic ZIP with root manifest and executable entry point', () => {
  expect(pack(stage, output).files).toBe(2);
  const first = readFileSync(output);
  pack(stage, output);
  expect(readFileSync(output)).toEqual(first);
  const entries = unzipSync(first);
  expect(Object.keys(entries).sort()).toEqual(['manifest.json', 'server/cli.cjs']);
  expect(JSON.parse(strFromU8(entries['manifest.json']))).toEqual(notes);
  const installed = join(root, 'installed.cjs');
  writeFileSync(installed, entries['server/cli.cjs']);
  const result = spawnSync(process.execPath, [installed], { cwd: root, encoding: 'utf8' });
  expect(result.status).toBe(0);
  expect(result.stdout.trim()).toBe('bundle launched');
});

test.each([
  { manifest_version: undefined }, { manifest_version: '0.4' }, { unexpected: true },
  { author: { name: 'test', email: 'not-an-email' } }, { homepage: 'not-a-uri' },
  { server: { ...notes.server, entry_point: '../escape.js' } },
  { server: { ...notes.server, entry_point: 'C:\\escape.js' } },
  { server: { ...notes.server, entry_point: '/escape.js' } },
])('rejects malformed manifests: %j', changes => {
  writeFileSync(manifest, JSON.stringify({ ...notes, ...changes }));
  expect(() => validateManifest(manifest)).toThrow();
  expect(() => pack(stage, output)).toThrow();
});

test('rejects malformed JSON and manifests above the byte limit', () => {
  writeFileSync(manifest, '{');
  expect(() => validateManifest(manifest)).toThrow();
  writeFileSync(manifest, ' '.repeat(limits.manifest + 1));
  expect(() => validateManifest(manifest)).toThrow('64 KB');
});

test.each(['.env', '.env.local', '.git', 'node_modules', 'data'])('rejects private or dependency paths: %s', name => {
  writeFileSync(join(stage, name), 'private');
  expect(() => pack(stage, output)).toThrow('private bundle path');
});

test('rejects missing entry points and outputs inside the staging directory', () => {
  expect(() => pack(stage, join(stage, 'out.mcpb'))).toThrow('outside');
  rmSync(join(stage, 'server/cli.cjs'));
  expect(() => pack(stage, output)).toThrow('entry point is missing');
});

test.each(['nested', '..inside', '..cache/nested'])('rejects output in contained directory %s before writing', directory => {
  mkdirSync(join(stage, directory), { recursive: true });
  const destination = join(stage, directory, 'out.mcpb');
  expect(() => pack(stage, destination)).toThrow('outside');
  expect(existsSync(destination)).toBe(false);
});

test('allows actual sibling directories, including names beginning with two dots', () => {
  for (const directory of ['sibling', '..sibling']) {
    mkdirSync(join(root, directory));
    expect(pack(stage, join(root, directory, 'out.mcpb')).files).toBe(2);
  }
});

test('bounds archive size before reading oversized files', () => {
  const large = join(stage, 'large.bin');
  writeFileSync(large, '');
  truncateSync(large, limits.bytes + 1);
  expect(() => pack(stage, output)).toThrow('64 MiB');
});

test('bounds archive entry count and nesting depth', () => {
  for (let i = 0; i < limits.files; i++) writeFileSync(join(stage, `file-${i}`), '');
  expect(() => pack(stage, output)).toThrow('too many entries');
  rmSync(stage, { recursive: true });
  mkdirSync(join(stage, ...Array(limits.depth + 1).fill('nested')), { recursive: true });
  writeFileSync(manifest, JSON.stringify(notes));
  expect(() => pack(stage, output)).toThrow('bundle path');
});

test.skipIf(process.platform === 'win32')('rejects symlinks, including a symlinked manifest', () => {
  const outside = join(root, 'private.txt');
  writeFileSync(outside, 'secret');
  symlinkSync(outside, join(stage, 'leak.txt'));
  expect(() => pack(stage, output)).toThrow('symlinks');
  rmSync(manifest);
  symlinkSync(outside, manifest);
  expect(() => validateManifest(manifest)).toThrow('regular file');
});

test('CLI reports invalid input with a nonzero exit code', () => {
  writeFileSync(manifest, '{}');
  const result = spawnSync(process.execPath, [fileURLToPath(new URL('./mcpb.mjs', import.meta.url)), 'validate', manifest], { encoding: 'utf8' });
  expect(result.status).toBe(1);
  expect(result.stderr).toContain('Invalid MCPB manifest');
});

test('lockfile cannot restore the vulnerable MCPB/Zod dependency path', () => {
  const lock = JSON.parse(readFileSync(new URL('../package-lock.json', import.meta.url), 'utf8'));
  const packages = Object.entries(lock.packages);
  expect(packages.some(([path]) => path.endsWith('/@anthropic-ai/mcpb'))).toBe(false);
  const zod = packages.filter(([path]) => path.endsWith('/zod'));
  expect(zod.length).toBeGreaterThan(0);
  for (const [, { version }] of zod) {
    const [major, minor, patch] = version.split('.').map(Number);
    expect(major > 4 || (major === 4 && (minor > 6 || (minor === 6 && patch >= 6)))).toBe(true);
  }
});
