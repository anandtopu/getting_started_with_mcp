/** Build a self-contained Node server from the shared TypeScript implementation. */
import { build } from 'esbuild';
import { licenses } from './bundle_licenses.mjs';
const result = await build({entryPoints:['distribution/npm/src/cli.ts'], outfile:'distribution/npm/dist/cli.cjs',
  bundle:true, platform:'node', format:'cjs', target:'node24', minify:false,
  banner:{js:'#!/usr/bin/env node'}, legalComments:'eof', metafile:true});
await licenses(result.metafile, 'distribution/npm/dist/THIRD_PARTY_LICENSES.txt');
console.log('Built the self-contained notes CLI.');
