import { expect, it } from 'vitest';
import { fetchObject, realDataServer, usagePage } from './real_data.ts';
import { inMemory } from './clients.ts';
import { callback, callbackParams } from './oauth.ts';

it('bounds query pages, validates dates and never accepts SQL text',()=>{
  expect(usagePage({limit:2}).rows).toHaveLength(2);
  for(const input of [{limit:0},{limit:51},{offset:-1},{start:"2025-08-01' OR 1=1 --"},{start:'2025-02-31'}])expect(()=>usagePage(input)).toThrow();
});

it('enforces response size and shape even for successful HTTP replies',async()=>{
  const url=new URL('https://fixture.invalid');
  await expect(fetchObject(url,async()=>Response.json({text:'x'.repeat(64000)}))).rejects.toThrow('64 KB');
  await expect(fetchObject(url,async()=>Response.json([]))).rejects.toThrow('must be an object');
  await expect(fetchObject(url,async()=>new Response('',{status:500}))).rejects.toThrow('API request failed');
});

it('external weather access requires explicit consent and a fixed destination',async()=>{
  const requests:URL[]=[];
  await inMemory(()=>realDataServer(undefined,async url=>{requests.push(new URL(String(url)));return Response.json({current:{temperature_2m:10}});}),async client=>{
    const args={latitude:40,longitude:-90};
    expect((await client.callTool({name:'weather',arguments:args})).isError).toBe(true);
    expect(requests).toHaveLength(0);
    expect((await client.callTool({name:'weather',arguments:{...args,allow_network:true}})).isError).not.toBe(true);
    expect(requests[0].origin).toBe('https://api.open-meteo.com');
  });
});

it('validates exact OAuth callbacks, issuer and one unambiguous state',()=>{
  const good=callback+'?code=fixture&state=expected&iss=https%3A%2F%2Fissuer.example';
  expect(callbackParams(good,'expected','https://issuer.example').get('code')).toBe('fixture');
  for(const bad of [good+'&state=duplicate',good.replace('state=expected','state=wrong'),good.replace('issuer.example','wrong.example'),good.replace('/callback','/elsewhere')])expect(()=>callbackParams(bad,'expected','https://issuer.example')).toThrow();
});
