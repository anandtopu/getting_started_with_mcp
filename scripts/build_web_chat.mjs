import { build } from 'esbuild';
import { licenses } from './bundle_licenses.mjs';
const result = await build({entryPoints:['common/web_ui/app.source.js'],outfile:'common/web_ui/app.js',bundle:true,
  minify:true,format:'esm',target:'es2022',legalComments:'eof',metafile:true});
await licenses(result.metafile, 'common/web_ui/THIRD_PARTY_LICENSES.txt');
console.log('Built Lumen Chat with the official AppBridge.');
