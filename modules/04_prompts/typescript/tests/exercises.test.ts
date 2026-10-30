import { test, expect } from 'vitest';
import { solve as solve1 } from '../solutions/01_practice.ts';
import { solve as solve2 } from '../solutions/02_apply.ts';
import { solve as solve3 } from '../solutions/03_stretch.ts';
test('complete_space case 1', () => { expect(Reflect.apply(solve1, null, ["eng"])).toEqual(["engineering"]); });
test('complete_space case 2', () => { expect(Reflect.apply(solve1, null, ["missing"])).toEqual([]); });
test('embedded_prompt case 1', () => { expect(Reflect.apply(solve2, null, ["wiki://engineering/page-01", "# Review"])).toEqual({"role": "user", "content": {"type": "resource", "resource": {"uri": "wiki://engineering/page-01", "mimeType": "text/markdown", "text": "# Review"}}}); });
test('complete_page case 1', () => { expect(Reflect.apply(solve3, null, ["page-01", {"space": "engineering"}])).toEqual(["page-01"]); });
test('complete_page case 2', () => { expect(Reflect.apply(solve3, null, ["page-", {}])).toEqual([]); });
