/** Launch only the reviewed local synthetic issuer; no secret is returned to this wrapper. */
import { execFileSync } from 'node:child_process';
import { resolve } from 'node:path';
import { root } from './data.ts';
export function authFixture(enterprise=false) {
  const python=resolve(root,process.platform==='win32'?'.venv/Scripts/python.exe':'.venv/bin/python');
  return execFileSync(python,['scripts/ts_auth.py',...(enterprise?['--enterprise']:[])],{cwd:root,encoding:'utf8',timeout:40000});
}
