import { test, expect } from 'vitest';
import { lesson } from '../../../../common/typescript/advanced_lessons.ts';
test.each([1,2,3])('Protocol architecture: example %s', async part=>{expect((await lesson(1,part)).status).toBe('PASS');},20000);
