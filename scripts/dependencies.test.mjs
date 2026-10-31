import { afterEach, beforeEach, expect, test } from 'vitest';
import { mkdtempSync, mkdirSync, readFileSync, readdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, relative } from 'node:path';
import { createRequire } from 'node:module';
import { URL } from 'node:url';
import { setImmediate } from 'node:timers/promises';
import { ESLint } from 'eslint';
import tseslint from 'typescript-eslint';
import { Client } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';

const require = createRequire(import.meta.url);
const filesystemEntry = require.resolve('@modelcontextprotocol/server-filesystem/dist/index.js');
const filesystemRequire = createRequire(filesystemEntry);
const { glob } = filesystemRequire('glob');
const { Minimatch } = filesystemRequire('minimatch');
let directory;
beforeEach(() => { directory = mkdtempSync(join(tmpdir(), 'lumen-dependencies-')); });
afterEach(() => rmSync(directory, { recursive: true, force: true }));
function file(path, content = '') {
  const parts = path.split('/');
  mkdirSync(join(directory, ...parts.slice(0, -1)), { recursive: true });
  writeFileSync(join(directory, ...parts), content);
}

test('ESLint discovers nested TypeScript, respects ignores, and supports project-service matching', async () => {
  file('tsconfig.json', JSON.stringify({ compilerOptions: { strict: true }, include: ['src/**/*.ts'] }));
  file('src/nested/check.ts', 'await 123;');
  file('typed.ts', 'await 456;');
  file('ignored/broken.ts', 'this is intentionally invalid');
  const eslint = new ESLint({ cwd: directory, overrideConfigFile: true, overrideConfig: [
    { ignores: ['**/ignored/**'] },
    { files: ['**/*.ts'], languageOptions: { parser: tseslint.parser, parserOptions: {
      tsconfigRootDir: directory, projectService: { allowDefaultProject: ['typed.ts'] },
    } }, plugins: { '@typescript-eslint': tseslint.plugin },
    rules: { '@typescript-eslint/await-thenable': 'error' } },
  ] });
  const results = await eslint.lintFiles(['**/*.ts']);
  expect(results.map(result => relative(directory, result.filePath).replaceAll('\\', '/')).sort())
    .toEqual(['src/nested/check.ts', 'typed.ts']);
  for (const result of results) {
    expect(result.fatalErrorCount).toBe(0);
    expect(result.messages.map(message => message.ruleId)).toEqual(['@typescript-eslint/await-thenable']);
  }
}, 20000);

test('reference filesystem server preserves wildcard exclusions and allowed-directory boundaries', async () => {
  file('allowed/notes/release.md', 'release');
  file('allowed/.hidden.md', 'visible with dot matching');
  file('allowed/private/secret.md', 'excluded');
  file('outside.md', 'outside');
  const client = new Client({ name: 'dependency-acceptance', version: '1.0' }, {
    versionNegotiation: { mode: { pin: '2026-07-28' } },
  });
  const allowed = join(directory, 'allowed');
  try {
    await client.connect(new StdioClientTransport({ command: process.execPath, args: [filesystemEntry, allowed] }));
    await client.discover();
    const result = await client.callTool({ name: 'search_files', arguments: {
      path: allowed, pattern: '**/*.md', excludePatterns: ['**/private/**'],
    } });
    expect(result.isError).not.toBe(true);
    const matches = result.structuredContent.content.split('\n').map(path => relative(allowed, path).replaceAll('\\', '/')).sort();
    expect(matches).toEqual(['.hidden.md', 'notes/release.md']);
    const denied = await client.callTool({ name: 'read_text_file', arguments: { path: join(directory, 'outside.md') } });
    expect(denied.isError).toBe(true);
  } finally { await client.close(); }
}, 20000);

test('glob traverses normally, but cancellation stops further directory reads', async () => {
  file('a/b/file.md'); file('a/c/other.md');
  expect((await glob('**/*.md', { cwd: directory })).map(path => path.replaceAll('\\', '/')).sort())
    .toEqual(['a/b/file.md', 'a/c/other.md']);
  const controller = new globalThis.AbortController();
  let reads = 0;
  const reason = new Error('test cancellation');
  const fs = { readdir(path, options, callback) {
    reads++;
    const entries = readdirSync(path, options);
    // Abort between starting a directory read and delivering its results.
    // Microtasks make continued post-cancellation traversal deterministic.
    Promise.resolve().then(() => { controller.abort(reason); callback(null, entries); });
  } };
  await expect(glob('**/*', { cwd: directory, fs, signal: controller.signal })).rejects.toThrow('test cancellation');
  await setImmediate();
  expect(reads).toBe(1);
});

test('minimatch bounds optimization-generated patterns', () => {
  const matcher = new Minimatch('a/**/../'.repeat(8) + 'target', { optimizationLevel: 2, braceExpandMax: 16 });
  expect(matcher.globParts.length).toBeLessThanOrEqual(16);
});

test('lockfile keeps every minimatch and glob instance on the reviewed patched releases', () => {
  const lock = JSON.parse(readFileSync(new URL('../package-lock.json', import.meta.url), 'utf8'));
  for (const [name, version] of [['minimatch', '11.0.3'], ['glob', '14.0.3']]) {
    const entries = Object.entries(lock.packages).filter(([path]) => path.endsWith('/' + name));
    expect(entries.length).toBeGreaterThan(0);
    for (const [, pkg] of entries) expect(pkg.version).toBe(version);
  }
});
