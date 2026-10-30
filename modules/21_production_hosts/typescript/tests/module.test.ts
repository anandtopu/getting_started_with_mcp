import { test, expect } from 'vitest';
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
test.each([1,2,3])('Production hosts: example %s', async part=>{expect((await lesson(21,part)).status).toBe('PASS');},20000);
