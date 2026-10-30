/** Run through: uv run python scripts/ts_oauth.py
 * The local synthetic authority exercises PKCE; no account or model key is needed.
 * Concepts/spec: ./README.md. Expected: read=true, wrong issuer/write scope rejected.
 */
import { oauthDemo } from '../../../common/typescript/oauth.ts';
const chunks:Buffer[]=[];let size=0;
for await(const chunk of process.stdin){size+=chunk.length;if(size>16000)throw new Error('Fixture input too large');chunks.push(chunk);}
try {console.log(JSON.stringify(await oauthDemo(JSON.parse(Buffer.concat(chunks).toString()))));}
catch(error) {console.error(error instanceof Error?error.message:'OAuth fixture failed.');process.exitCode=1;}
