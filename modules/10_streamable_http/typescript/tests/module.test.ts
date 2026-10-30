import { test } from 'vitest';
import { withRemote, headerLab, recoveryLab } from '../../../../common/typescript/remote_client.ts';

test('HTTP header enforcement and CORS', async () => { await withRemote(headerLab); });
test('shared state, duplicate write and reconnect', async () => { await withRemote(recoveryLab); });
