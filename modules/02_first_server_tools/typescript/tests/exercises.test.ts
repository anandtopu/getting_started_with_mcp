import { test, expect } from 'vitest';
import { solve as solve1 } from '../solutions/01_practice.ts';
import { solve as solve2 } from '../solutions/02_apply.ts';
import { solve as solve3 } from '../solutions/03_stretch.ts';
test('input_schema case 1', () => { expect(Reflect.apply(solve1, null, [])).toEqual({"type": "object", "properties": {"name": {"type": "string", "minLength": 1}}, "required": ["name"]}); });
test('confirm_write case 1', () => { expect(Reflect.apply(solve2, null, [false])).toEqual({"content": [{"type": "text", "text": "Confirmation required"}], "isError": true}); });
test('confirm_write case 2', () => { expect(Reflect.apply(solve2, null, [true])).toEqual({"content": [{"type": "text", "text": "Saved"}], "isError": false}); });
test('unique_tags case 1', () => { expect(Reflect.apply(solve3, null, [["release"], "release"])).toEqual(["release"]); });
test('unique_tags case 2', () => { expect(Reflect.apply(solve3, null, [["release"], "review"])).toEqual(["release", "review"]); });
