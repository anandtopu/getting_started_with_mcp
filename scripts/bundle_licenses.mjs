/** Preserve full dependency notices for packages actually included by esbuild. */
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

export async function licenses(meta, output) {
  const packages = new Map();
  for (const input of Object.keys(meta.inputs)) {
    if (!input.includes('node_modules/')) continue;
    let folder = dirname(resolve(input));
    while (folder !== dirname(folder)) {
      try {
        const data = JSON.parse(await readFile(resolve(folder, 'package.json'), 'utf8'));
        // Some libraries use tiny nested package.json files only to set module type.
        if (!data.name) { folder = dirname(folder); continue; }
        packages.set(data.name, { folder, version: data.version, license: data.license });
        break;
      } catch { folder = dirname(folder); }
    }
  }
  const texts = [];
  for (const [name, entry] of [...packages.entries()].sort()) {
    let license = '';
    for (const file of ['LICENSE', 'LICENSE.md', 'LICENSE.txt', 'license', 'license.md']) {
      try { license = await readFile(resolve(entry.folder, file), 'utf8'); break; } catch { /* next */ }
    }
    if (!license) throw new Error(`Missing license text for bundled package ${name}`);
    texts.push(`${name} ${entry.version} (${entry.license})\n\n${license}`);
  }
  await writeFile(output, texts.join('\n\n========================================\n\n'));
}
