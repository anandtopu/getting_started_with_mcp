/** Expand only local $defs references, with the same bounds as the Python host. */
import { Ajv2020 } from 'ajv/dist/2020.js';
import type { Tool } from '@modelcontextprotocol/client';

export function modelTool(tool:Tool):Tool {
  const source=structuredClone(tool.inputSchema);let nodes=0;
  function visit(value:unknown,depth=0,trail:string[]=[]):unknown {
    if(++nodes>1000 || depth>12)throw new Error('Schema size or depth limit exceeded.');
    if(Array.isArray(value))return value.map(item=>visit(item,depth+1,trail));
    if(!value || typeof value!=='object')return value;
    const entry=value as Record<string,unknown>;
    if('$dynamicRef' in entry || '$recursiveRef' in entry)throw new Error('Dynamic and recursive schema references are unsupported.');
    if('$ref' in entry) {
      const ref=entry.$ref;
      if(typeof ref!=='string' || !ref.startsWith('#/$defs/') || trail.includes(ref))throw new Error('Only non-recursive local schema references are supported.');
      const target=(source.$defs as Record<string,unknown>|undefined)?.[ref.slice(8)];
      if(!target || typeof target!=='object')throw new Error('Missing local schema definition.');
      const resolved=visit(target,depth+1,[...trail,ref]);
      const siblings=Object.fromEntries(Object.entries(entry).filter(([k])=>k!=='$ref').map(([k,v])=>[k,visit(v,depth+1,trail)]));
      return Object.keys(siblings).length?{allOf:[resolved,siblings]}:resolved;
    }
    return Object.fromEntries(Object.entries(entry).filter(([k])=>k!=='$defs').map(([k,v])=>[k,visit(v,depth+1,trail)]));
  }
  const schema=visit(source) as Tool['inputSchema'];
  if(schema.properties)delete schema.properties.confirmed;
  schema.required=schema.required?.filter(key=>key!=='confirmed')??[];
  schema.additionalProperties=false;
  return {...structuredClone(tool),inputSchema:schema};
}

export function validateProposal(tool:Tool,args:unknown) {
  const ajv=new Ajv2020({strict:false,validateFormats:false});
  if(!ajv.validate(modelTool(tool).inputSchema,args))throw new Error('Invalid arguments: use the advertised schema; confirmation belongs to the host.');
}
