/** Native module 18 lab: build, inspect, install and launch outside the checkout. */
import { strict as assert } from 'node:assert';
import { Buffer } from 'node:buffer';
import { mkdtempSync, realpathSync, existsSync, mkdirSync, copyFileSync, readFileSync, writeFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve, relative, sep, isAbsolute } from 'node:path';
import { fileURLToPath, URL } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { Client } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';
import { unzipSync } from 'fflate';
import { pack, validateManifest } from './mcpb.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const run = promisify(execFile);
const npmFiles = ['LICENSE', 'README.md', 'dist/THIRD_PARTY_LICENSES.txt', 'dist/cli.cjs', 'package.json'];
const bundleFiles = ['LICENSE', 'THIRD_PARTY_LICENSES.txt', 'manifest.json', 'server/cli.cjs'];

function npmCli() {
  const bin = dirname(realpathSync(process.execPath));
  const candidates = [process.env.npm_execpath, join(bin, 'node_modules/npm/bin/npm-cli.js'),
    resolve(bin, '../lib/node_modules/npm/bin/npm-cli.js')];
  const cli = candidates.find(path => path && existsSync(path));
  if (!cli) throw new Error('Cannot locate npm CLI. Run this lesson through npm exec -- tsx <example.ts>.');
  return cli;
}

async function command(args, cwd) {
  const result = await run(process.execPath, args, { cwd, timeout: 120000, maxBuffer: 2 * 1024 * 1024, windowsHide: true });
  return result.stdout;
}

function inventory(directory, prefix = '') {
  return readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    assert.ok(!entry.isSymbolicLink(), 'No symlinks in the installed package');
    return entry.isDirectory() ? inventory(join(directory, entry.name), prefix + entry.name + '/') : [prefix + entry.name];
  }).sort();
}

async function smoke(args, cwd) {
  const client = new Client({ name: 'Lumen installed package check', version: '1' }, {
    versionNegotiation: { mode: { pin: '2026-07-28' } },
  });
  const transport = new StdioClientTransport({ command: process.execPath, args, cwd,
    env: { LUMEN_NOTES_READ_ONLY: 'true' }, stderr: 'pipe' });
  try {
    await client.connect(transport);await client.discover();
    assert.deepEqual((await client.listTools()).tools.map(tool => tool.name), ['search_notes']);
    const result = await client.callTool({ name: 'search_notes', arguments: { query: 'release' } });
    assert.ok(!result.isError);
    assert.equal(result.structuredContent.result[0].title, 'Release handover');
    return { tools: ['search_notes'], matches: result.structuredContent.result.length };
  } finally { await client.close();await transport.close(); }
}

export async function packagingLesson(kind) {
  if (!['npm', 'mcpb'].includes(kind)) throw new Error('Choose npm or mcpb');
  // Canonicalize Windows short temp paths before checking the working-directory boundary.
  const temporary = realpathSync.native(mkdtempSync(join(tmpdir(), 'lumen-ts-package-')));
  try {
    const outside = relative(realpathSync.native(root), temporary);
    assert.ok(outside === '..' || outside.startsWith('..' + sep) || isAbsolute(outside));
    const source = join(temporary, 'source');
    const cwd = join(temporary, 'empty-working-directory');mkdirSync(cwd);
    mkdirSync(source);
    for (const name of ['package.json', 'README.md', 'LICENSE']) copyFileSync(join(root, 'distribution/npm', name), join(source, name));
    await command([join(root, 'scripts/build_notes.mjs'), join(source, 'dist/cli.cjs')], root);
    if (kind === 'npm') {
      const cli = npmCli();
      const [metadata] = JSON.parse(await command([cli, 'pack', source, '--json', '--ignore-scripts', '--pack-destination', temporary], temporary));
      assert.deepEqual(metadata.files.map(file => file.path).sort(), npmFiles);
      const installed = join(temporary, 'installed');mkdirSync(installed);
      await command([cli, 'install', '--prefix', installed, '--offline', '--ignore-scripts', '--no-audit', '--no-fund', '--package-lock=false', join(temporary, metadata.filename)], temporary);
      const packageRoot = join(installed, 'node_modules', metadata.name);
      assert.deepEqual(inventory(packageRoot), npmFiles);
      for (const name of npmFiles) assert.deepEqual(readFileSync(join(packageRoot, name)), readFileSync(join(source, name)));
      const launch = await smoke([cli, 'exec', '--offline', '--prefix', installed, '--', 'lumen-notes'], cwd);
      return { kind, version: metadata.version, files: npmFiles, outside_checkout: true, ...launch };
    }
    const stage = join(temporary, 'bundle');mkdirSync(join(stage, 'server'), { recursive: true });
    copyFileSync(join(root, 'distribution/mcpb/manifest.json'), join(stage, 'manifest.json'));
    copyFileSync(join(source, 'dist/cli.cjs'), join(stage, 'server/cli.cjs'));
    copyFileSync(join(source, 'dist/THIRD_PARTY_LICENSES.txt'), join(stage, 'THIRD_PARTY_LICENSES.txt'));
    copyFileSync(join(source, 'LICENSE'), join(stage, 'LICENSE'));
    validateManifest(join(stage, 'manifest.json'));
    const archive = join(temporary, 'notes.mcpb');pack(stage, archive);
    const entries = unzipSync(readFileSync(archive));
    assert.deepEqual(Object.keys(entries).sort(), bundleFiles);
    const extracted = join(temporary, 'extracted');mkdirSync(join(extracted, 'server'), { recursive: true });
    // Only extract the exact, inspected allowlist from our just-built archive.
    for (const name of bundleFiles) {
      assert.deepEqual(Buffer.from(entries[name]), readFileSync(join(stage, name)));
      writeFileSync(join(extracted, name), entries[name]);
    }
    const manifest = validateManifest(join(extracted, 'manifest.json'));
    const launch = await smoke([join(extracted, manifest.server.entry_point)], cwd);
    return { kind, version: manifest.version, files: bundleFiles, outside_checkout: true, ...launch };
  } finally { rmSync(temporary, { recursive: true, force: true }); }
}
