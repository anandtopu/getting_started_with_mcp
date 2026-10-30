/** Small policy mechanisms used by the full TypeScript track. */
import { createPublicKey, generateKeyPairSync, sign, verify, randomBytes, type KeyObject } from 'node:crypto';
import { z } from 'zod';

const claimsSchema = z.object({ iss:z.string(), aud:z.string(), sub:z.string().min(1), exp:z.number(), iat:z.number(), scope:z.string() }).strict();
export type Claims = z.infer<typeof claimsSchema>;
export function fixtureKeys() { return generateKeyPairSync('rsa', { modulusLength:2048 }); }
export function mintToken(claims: Claims, key: KeyObject) {
  const data = [Buffer.from(JSON.stringify({alg:'RS256',typ:'JWT'})).toString('base64url'),Buffer.from(JSON.stringify(claims)).toString('base64url')].join('.');
  return `${data}.${sign('RSA-SHA256',Buffer.from(data),key).toString('base64url')}`;
}
export function verifyToken(token:string, key:KeyObject, issuer:string, audience:string, now=Date.now()/1000):Claims {
  if(token.length>16000) throw new Error('Token too large');
  const parts=token.split('.');
  if(parts.length!==3) throw new Error('Invalid token');
  const header=JSON.parse(Buffer.from(parts[0],'base64url').toString());
  if(header.alg!=='RS256' || !verify('RSA-SHA256',Buffer.from(`${parts[0]}.${parts[1]}`),key,Buffer.from(parts[2],'base64url'))) throw new Error('Invalid signature');
  const claims=claimsSchema.parse(JSON.parse(Buffer.from(parts[1],'base64url').toString()));
  if(claims.iss!==issuer || claims.aud!==audience || claims.exp<=now || claims.iat>now+30) throw new Error('Invalid issuer, audience or expiry');
  return claims;
}
export { createPublicKey };
export class RateLimit {
  private windows=new Map<string,number[]>();
  constructor(readonly limit=60, readonly clock=()=>Date.now()) {}
  allow(subject:string) {
    const now=this.clock();
    for(const [k,v] of this.windows) { const fresh=v.filter(t=>t>now-60000); if(fresh.length) this.windows.set(k,fresh); else this.windows.delete(k); }
    if(!this.windows.has(subject) && this.windows.size>=100) return false;
    const window=this.windows.get(subject)??[];
    if(window.length>=this.limit) return false;
    window.push(now);this.windows.set(subject,window);return true;
  }
}
export class ReviewLedger {
  private pending=new Map<string,{binding:string;expires:number}>();
  issue(binding:string) {
    for(const [k,v] of this.pending) if(v.expires<Date.now()) this.pending.delete(k);
    if(this.pending.size>=100) throw new Error('Review capacity reached');
    const key=randomBytes(24).toString('base64url');this.pending.set(key,{binding,expires:Date.now()+60000});return key;
  }
  take(key:string,binding:string) {
    const value=this.pending.get(key);this.pending.delete(key);
    if(!value || value.binding!==binding || value.expires<Date.now()) throw new Error('Unknown, changed or expired review');
  }
}
export function redact(value:unknown):unknown {
  if(Array.isArray(value)) return value.map(redact);
  if(value && typeof value==='object') return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,/token|secret|authorization|assertion|password/i.test(k)?'[REDACTED]':redact(v)]));
  return value;
}
export function publicEndpoint(value:string) {
  const u=new URL(value);
  if(u.username || u.password || u.hash || u.search || (u.protocol!=='https:' && !(u.protocol==='http:' && ['localhost','127.0.0.1'].includes(u.hostname)))) throw new Error('Use HTTPS or exact loopback without credentials');
  return u.href;
}
