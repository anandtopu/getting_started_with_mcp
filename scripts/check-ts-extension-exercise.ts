/** Check one B1 exercise. Run: node --import tsx scripts/check-ts-extension-exercise.ts 6 1 [--solution] */
import { strict as assert } from 'node:assert';
import { readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { root } from '../common/typescript/data.ts';
import { practice } from '../common/typescript/exercise_contracts.ts';
const [moduleText,number]=process.argv.slice(2);
const folder=readdirSync(resolve(root,'modules')).find(n=>n.startsWith(`${Number(moduleText).toString().padStart(2,'0')}_`));
if(!folder || !practice[Number(moduleText)] || !['1','2','3'].includes(number))throw new Error('Choose module 00–21 and exercise 1–3');
const names=['bounded','review','pages'];
const path=resolve(root,'modules',folder,'typescript',process.argv.includes('--solution')?'solutions':'exercises',`${number.padStart(2,'0')}_${names[Number(number)-1]}.ts`);
const {solve}=await import(pathToFileURL(path).href);
try {
  if(number==='1')for(const {value,expected,want} of practice[Number(moduleText)] ?? [])assert.equal(solve(value,expected),want);
  if(number==='2')for(const [a,b,ok,want] of [['v1','v1',true,true],['v1','v2',true,false],['v1','v1',false,false],['','',true,false]])assert.equal(solve(a,b,ok),want);
  if(number==='3'){assert.equal(solve([undefined]),1);assert.equal(solve(['a',undefined]),2);assert.throws(()=>solve(['a','a']));assert.throws(()=>solve([]));assert.throws(()=>solve(Array.from({length:21},(_,i)=>String(i))));}
  console.log('PASS exercise');
}catch {console.error('Exercise mismatch. Review the contract in the TypeScript README; --solution checks the reference.');process.exitCode=1;}
