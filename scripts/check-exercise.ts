/** Run: npm exec tsx -- scripts/check-exercise.ts 2 1 [--solution] */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { deepStrictEqual } from 'node:assert';
import { root } from '../common/typescript/data.ts';

const modules: Record<string, string> = { '2': '02_first_server_tools', '3': '03_resources', '4': '04_prompts', '5': '05_first_client', '10': '10_streamable_http' };
const [module, exercise] = process.argv.slice(2);
if (!modules[module] || !['1', '2', '3'].includes(exercise)) throw new Error('Use module 2–5 or 10 and exercise 1–3.');
const folder = resolve(root, 'modules', modules[module]);
const contracts = JSON.parse(readFileSync(resolve(folder, 'python/tests/exercise_cases.json'), 'utf8'));
const contract = contracts[Number(exercise) - 1];
const target = process.argv.includes('--solution') ? 'solutions' : 'exercises';
const { solve } = await import(pathToFileURL(resolve(folder, 'typescript', target, `${contract.stem}.ts`)).href);
for (const [args, expected] of contract.cases) deepStrictEqual(Reflect.apply(solve, null, args), expected, contract.task);
console.log('Exercise checks passed.');
