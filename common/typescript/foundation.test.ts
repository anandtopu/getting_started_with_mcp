import { describe, expect, it } from 'vitest';
import { resolve } from 'node:path';
import { employees, root, safePath } from './data.ts';
import { provider } from './config.ts';
import { originAllowed } from './testing.ts';

describe('shared fixture and policy contracts', () => {
  it('reads all synthetic employees', () => expect(employees()).toHaveLength(80));
  it('rejects escape paths', () => expect(() => safePath(resolve(root, 'data'), '../.env')).toThrow());
  it('defaults to an offline provider', () => expect(provider({})).toBe('fake'));
  it('rejects unknown providers', () => expect(() => provider({LLM_PROVIDER:'invalid'})).toThrow());
  it('checks browser origins exactly', () => {
    expect(originAllowed('http://localhost.evil.invalid', ['http://localhost'])).toBe(false);
    expect(originAllowed(undefined, [])).toBe(true);
  });
});
