// Course-only MCPB 0.3 validator/packer. No install, unpack, signing or script execution.
import { readFileSync, lstatSync, readdirSync, realpathSync, writeFileSync, renameSync, rmSync } from 'node:fs';
import { resolve, dirname, basename, join, relative, isAbsolute, sep } from 'node:path';
import { fileURLToPath, URL } from 'node:url';
import { randomUUID } from 'node:crypto';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import { zipSync } from 'fflate';

export const limits = Object.freeze({ manifest: 64000, bytes: 64 * 1024 * 1024, files: 512, depth: 16 });
const ajv = new Ajv({ allErrors: false, strict: true });
addFormats(ajv);
const validate = ajv.compile(JSON.parse(readFileSync(new URL('../distribution/mcpb/schema/manifest-v0.3.schema.json', import.meta.url), 'utf8')));
const forbidden = new Set(['.env', '.git', 'node_modules', '__pycache__', '.venv', 'data']);

function safePath(name) {
  const parts = name.split('/');
  if (!name || parts.length > limits.depth || parts.some(part => !part || part === '.' || part === '..'
    || forbidden.has(part.toLowerCase()) || part.toLowerCase().startsWith('.env.')
    || /[\\:]/.test(part) || [...part].some(char => char.charCodeAt(0) < 32) || /[. ]$/.test(part)
    || /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(part))) {
    throw new Error('Unsafe or private bundle path');
  }
}

export function validateManifest(path) {
  const stat = lstatSync(path);
  if (!stat.isFile() || stat.size > limits.manifest) throw new Error('Manifest must be a regular file of at most 64 KB');
  const manifest = JSON.parse(readFileSync(path, 'utf8'));
  if (!validate(manifest)) throw new Error(`Invalid MCPB manifest: ${ajv.errorsText(validate.errors)}`);
  // The upstream Zod refinement is not represented in its generated JSON Schema.
  if (manifest.manifest_version !== '0.3') throw new Error('Course bundles require manifest_version 0.3');
  safePath(manifest.server.entry_point);
  return manifest;
}

export function pack(source, destination) {
  if (!lstatSync(source).isDirectory()) throw new Error('Bundle source must be a regular directory');
  const root = realpathSync(source);
  const output = join(realpathSync(dirname(resolve(destination))), basename(destination));
  const rel = relative(root, output);
  if (!(rel === '..' || rel.startsWith('..' + sep) || isAbsolute(rel))) throw new Error('Output must be outside the bundle directory');
  const manifest = validateManifest(join(root, 'manifest.json'));
  const files = Object.create(null);
  const names = new Set();
  let bytes = 0;
  let count = 0;
  function walk(directory, prefix = '') {
    for (const name of readdirSync(directory).sort()) {
      const archivePath = prefix + name;
      safePath(archivePath);
      if (++count > limits.files) throw new Error('Bundle contains too many entries');
      const path = join(directory, name);
      const stat = lstatSync(path);
      if (stat.isSymbolicLink()) throw new Error('Bundle symlinks are forbidden');
      if (names.has(archivePath.toLowerCase())) throw new Error('Bundle paths must be unique across platforms');
      names.add(archivePath.toLowerCase());
      if (stat.isDirectory()) walk(path, archivePath + '/');
      else {
        if (!stat.isFile()) throw new Error('Bundle contains a non-regular file');
        bytes += stat.size;
        if (bytes > limits.bytes) throw new Error('Bundle exceeds 64 MiB');
        files[archivePath] = [readFileSync(path), { mtime: new Date(2000, 0, 1), level: 6 }];
      }
    }
  }
  walk(root);
  if (!Object.hasOwn(files, manifest.server.entry_point)) throw new Error('Bundle entry point is missing');
  const temporary = output + '.' + randomUUID() + '.tmp';
  try {
    writeFileSync(temporary, zipSync(files), { flag: 'wx' });
    renameSync(temporary, output);
  } finally {
    rmSync(temporary, { force: true });
  }
  return { files: Object.keys(files).length, bytes };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const [command, source, destination, ...extra] = process.argv.slice(2);
    if (command === 'validate' && source && !destination) {
      validateManifest(source);
      console.log('MCPB 0.3 manifest valid');
    } else if (command === 'pack' && source && destination && !extra.length) {
      console.log(JSON.stringify(pack(source, destination)));
    } else throw new Error('Usage: npm run mcpb -- validate <manifest.json> | pack <staged-directory> <output.mcpb>');
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
