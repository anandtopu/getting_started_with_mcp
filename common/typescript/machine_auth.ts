/** Actual SDK providers against the synthetic loopback issuer. Never logs secrets. */
import { ClientCredentialsProvider, CrossAppAccessProvider } from '@modelcontextprotocol/client';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/client';
import { newClient } from './clients.ts';
import { strict as assert } from 'node:assert';
import { z } from 'zod';

export async function machineDemo(config:unknown) {
  const c=z.object({issuer:z.url(),resource:z.url(),secret:z.string(),assertion:z.string().optional()}).parse(config);
  // Credentials arrive over stdin from our local fixture, never from an untrusted card.
  for(const value of [c.issuer,c.resource]) if(new URL(value).hostname!=='127.0.0.1') throw new Error('Fixture requires exact loopback');
  const common={clientId:'lumen-machine',clientSecret:c.secret,expectedIssuer:c.issuer};
  const authProvider=c.assertion?new CrossAppAccessProvider({...common,assertion:async ctx=>{assert.equal(ctx.authorizationServerUrl,c.issuer);assert.equal(ctx.resourceUrl,c.resource);return c.assertion!;}}):new ClientCredentialsProvider({...common,scope:'issues:read'});
  const transport=new StreamableHTTPClientTransport(new URL(c.resource),{authProvider});
  const client=newClient();
  try {await client.connect(transport);await client.discover();for(const id of [1,2])assert.ok(!(await client.callTool({name:'read_issue',arguments:{issue_id:id}})).isError);}
  finally {await client.close();}
  return {flow:c.assertion?'enterprise ID-JAG leg 2':'client credentials',vendor_sso_tested:false};
}
