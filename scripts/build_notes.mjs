/** Build a self-contained Node server from the shared TypeScript implementation. */
import { build } from 'esbuild';
import { licenses } from './bundle_licenses.mjs';
import { dirname, join, resolve } from 'node:path';
const output = resolve(process.argv[2] ?? 'distribution/npm/dist/cli.cjs');
const result = await build({entryPoints:['distribution/npm/src/cli.ts'], outfile:output,
  bundle:true, platform:'node', format:'cjs', target:'node24', minify:false,
  banner:{js:'#!/usr/bin/env node'}, legalComments:'eof', metafile:true});
await licenses(result.metafile, join(dirname(output), 'THIRD_PARTY_LICENSES.txt'));
console.log('Built the self-contained notes CLI.');
