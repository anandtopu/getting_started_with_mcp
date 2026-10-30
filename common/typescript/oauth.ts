/** Native SDK discovery, PKCE and issuer-bound tokens against the local OAuth lab. */
import { randomBytes, timingSafeEqual } from 'node:crypto';
import { strict as assert } from 'node:assert';
import { StreamableHTTPClientTransport, type OAuthClientProvider, type OAuthClientInformationContext, type StoredOAuthTokens } from '@modelcontextprotocol/client';
import { z } from 'zod';
import { newClient } from './clients.ts';

export const callback='http://127.0.0.1:8765/callback';
export function callbackParams(value:string,state:string,issuer:string) {
  const url=new URL(value);
  if(url.origin+url.pathname!==callback || url.hash || [...url.searchParams.keys()].some(key=>url.searchParams.getAll(key).length!==1))throw new Error('Invalid callback URL.');
  const received=Buffer.from(url.searchParams.get('state')??'');const expected=Buffer.from(state);
  if(received.length!==expected.length || !timingSafeEqual(received,expected))throw new Error('Authorization state mismatch.');
  if(url.searchParams.get('iss')!==issuer)throw new Error('Authorization issuer mismatch.');
  if(url.searchParams.has('error') || !url.searchParams.get('code'))throw new Error('Authorization was not granted.');
  return url.searchParams;
}

class FixtureProvider implements OAuthClientProvider {
  readonly redirectUrl=callback;
  readonly clientMetadata={redirect_uris:[callback],token_endpoint_auth_method:'none',grant_types:['authorization_code'],response_types:['code'],scope:'issues:read'};
  private saved?:StoredOAuthTokens;
  private verifier='';
  private nonce=randomBytes(24).toString('base64url');
  authorization?:URL;
  constructor(readonly issuer:string,readonly resource:string) {}
  private bind(context?:OAuthClientInformationContext){if(context && context.issuer!==this.issuer)throw new Error('Unreviewed authorization server.');}
  clientInformation(context?:OAuthClientInformationContext){this.bind(context);return {client_id:'lumen-chat',issuer:this.issuer};}
  tokens(context?:OAuthClientInformationContext){this.bind(context);return this.saved;}
  saveTokens(tokens:StoredOAuthTokens,context?:OAuthClientInformationContext){this.bind(context);this.saved=tokens;}
  state(){return this.nonce;}
  saveCodeVerifier(value:string){this.verifier=value;}
  codeVerifier(){return this.verifier;}
  redirectToAuthorization(url:URL) {
    if(url.origin!==this.issuer || url.pathname!=='/authorize' || url.searchParams.get('resource')!==this.resource || url.searchParams.get('code_challenge_method')!=='S256')throw new Error('Unexpected authorization request.');
    this.authorization=url;
  }
  async consentFixture() {
    if(!this.authorization)throw new Error('Discovery did not request authorization.');
    const page=await fetch(this.authorization,{redirect:'error',signal:AbortSignal.timeout(5000)});
    if(!page.ok)throw new Error('Fixture authorization page unavailable.');
    const action=/action="(\/consent\?ticket=[A-Za-z0-9_-]+)"/.exec(await page.text())?.[1];
    if(!action)throw new Error('Fixture consent form missing.');
    const consent=await fetch(this.issuer+action,{method:'POST',redirect:'manual',signal:AbortSignal.timeout(5000)});
    if(consent.status!==302)throw new Error('Fixture consent failed.');
    return callbackParams(consent.headers.get('location')??'',this.nonce,this.issuer);
  }
}

export async function oauthDemo(input:unknown) {
  const config=z.object({issuer:z.url(),resource:z.url()}).strict().parse(input);
  for(const value of [config.issuer,config.resource]) {
    const url=new URL(value);
    if(url.protocol!=='http:' || url.hostname!=='127.0.0.1' || url.username || url.password || url.search || url.hash)throw new Error('Synthetic fixture requires exact loopback.');
  }
  const provider=new FixtureProvider(config.issuer,config.resource);
  const transport=new StreamableHTTPClientTransport(new URL(config.resource),{authProvider:provider});
  let client=newClient();let stage="connect";
  try {
    await assert.rejects(async()=>{await client.connect(transport);await client.discover();});
    stage="consent";const params=await provider.consentFixture();
    const wrong=new URLSearchParams(params);wrong.set('iss','https://wrong.example');
    stage="wrong issuer";await assert.rejects(transport.finishAuth(wrong));
    stage="exchange";await transport.finishAuth(params);
    await client.close();client=newClient();
    stage="authenticated discovery";await client.connect(new StreamableHTTPClientTransport(new URL(config.resource),{authProvider:provider}));await client.discover();
    stage='read';assert.equal((await client.callTool({name:'read_issue',arguments:{issue_id:1}})).isError===true,false);
    stage='write rejection';await assert.rejects(client.callTool({name:'create_issue',arguments:{issue:{title:'Must be denied'},operation_key:'no-scope',confirmed:true}}));
    assert.equal(provider.tokens()?.scope,'issues:read');
    return {flow:'native authorization code + PKCE',read:true,wrong_issuer_rejected:true,write_scope_denied:true};
  }catch(error){throw new Error(`OAuth ${stage}: ${error instanceof Error?error.name:"failure"}`,{cause:error});}finally{await client.close();}
}
