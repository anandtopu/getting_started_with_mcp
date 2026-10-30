import { test, expect } from 'vitest';
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
test.each([1,2,3])('Security boundaries: example %s', async part=>{expect((await lesson(12,part)).status).toBe('PASS');},20000);
