import { it, expect } from 'vitest';
import { readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { practice } from './exercise_contracts.ts';
import { root } from './data.ts';

it.each(Object.keys(practice).map(Number))('module %i exercise solutions meet independent contracts', async module => {
  const folder = readdirSync(resolve(root, 'modules')).find(n => n.startsWith(`${String(module).padStart(2,'0')}_`))!;
  const load = (file:string) => import(pathToFileURL(resolve(root,'modules',folder,'typescript/solutions',file)).href);
  const { solve: boundary } = await load('01_bounded.ts');
  for (const {value,expected,want} of practice[module]) expect(boundary(value,expected)).toBe(want);
  const { solve: review } = await load('02_review.ts');
  expect(review('v1','v1',true)).toBe(true);
  expect(review('v1','v2',true)).toBe(false);
  expect(review('v1','v1',false)).toBe(false);
  expect(review('','',true)).toBe(false);
  const { solve: pages } = await load('03_pages.ts');
  expect(pages([undefined])).toBe(1);
  expect(pages(['a',undefined])).toBe(2);
  expect(() => pages(['a','a'])).toThrow();
  expect(() => pages([])).toThrow();
  expect(() => pages(Array.from({length:21},(_,i)=>String(i)))).toThrow();
});
