import { test, expect } from 'vitest';
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
test.each([1,2,3])('Composition: example %s', async part=>{expect((await lesson(16,part)).status).toBe('PASS');},20000);
