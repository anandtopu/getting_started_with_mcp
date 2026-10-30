import { test, expect } from 'vitest';
import { solve as solve1 } from '../solutions/01_practice.ts';
import { solve as solve2 } from '../solutions/02_apply.ts';
import { solve as solve3 } from '../solutions/03_stretch.ts';
test('resource_uri case 1', () => { expect(Reflect.apply(solve1, null, ["engineering", "page-01"])).toEqual("wiki://engineering/page-01"); });
test('resource_uri case 2', () => { expect(Reflect.apply(solve1, null, ["engineering", "../secret"])).toEqual(null); });
test('content_field case 1', () => { expect(Reflect.apply(solve2, null, ["text/markdown"])).toEqual("text"); });
test('content_field case 2', () => { expect(Reflect.apply(solve2, null, ["application/pdf"])).toEqual("blob"); });
test('invalidate_resource case 1', () => { expect(Reflect.apply(solve3, null, [{"wiki://index": "index", "lumen://bulletin": "old"}, "lumen://bulletin"])).toEqual({"wiki://index": "index"}); });
