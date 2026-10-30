/** Validate the vendored experimental card schema, then apply a separate trust policy. */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { Ajv2020 } from 'ajv/dist/2020.js';
import { root } from './data.ts';
import { publicEndpoint } from './advanced_policy.ts';

export const cardBase=resolve(root,'modules/bonus/B4_whats_new/data');
export function validateCard(card:unknown, trustedHost:string) {
  const schema=JSON.parse(readFileSync(resolve(cardBase,'server-card.schema.json'),'utf8'));
  const ajv=new Ajv2020({strict:false,validateFormats:false});
  const validate=ajv.compile({...schema,$ref:'#/$defs/ServerCard'});
  if(!validate(card))throw new Error('Server Card schema invalid');
  const value=card as {name:string;remotes?:{url:string;headers?:unknown[]}[]};
  if(!value.remotes?.length)throw new Error('Select an explicit remote endpoint');
  for(const remote of value.remotes) {
    const url=new URL(publicEndpoint(remote.url));
    if(url.protocol!=='https:' || url.hostname!==trustedHost || remote.headers?.length)throw new Error('Review endpoint and header requests before connecting');
  }
  return {name:value.name,candidate_count:value.remotes.length,connected:false};
}
