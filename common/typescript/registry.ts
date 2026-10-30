/** Validate the actual pinned Registry schema; metadata never authorizes install. */
import { Ajv } from 'ajv';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { root } from './data.ts';

const readJSON=(path:string)=>JSON.parse(readFileSync(resolve(root,path),'utf8'));
export function validateMetadata(document=readJSON('distribution/registry/server.json')) {
  const schema=readJSON('distribution/registry/server.schema.json');
  const ajv=new Ajv({strict:false,allErrors:true});
  ajv.addFormat('uri',(value:string)=>{try {return Boolean(new URL(value).protocol);}catch{return false;}});
  if(!ajv.validate(schema,document))throw new Error('Registry schema validation failed: '+ajv.errorsText());
  const pkg=readJSON('distribution/npm/package.json');
  const value=document as {$schema:string;name:string;version:string;packages?:{identifier:string}[]};
  if(value.$schema!==schema.$id || value.name!==pkg.mcpName || value.version!==pkg.version || value.packages?.[0]?.identifier!==pkg.name)throw new Error('Registry identity/version must match the package being published.');
  return value;
}

export async function registryPages(fetchPage:(cursor?:string)=>Promise<{servers:unknown[];metadata?:{nextCursor?:string}}>) {
  const records:unknown[]=[];const seen=new Set<string>();let cursor:string|undefined;
  for(let page=0;page<3;page++) {
    const value=await fetchPage(cursor);records.push(...value.servers);
    cursor=value.metadata?.nextCursor;
    if(cursor===undefined)return records;
    if(!cursor || cursor.length>2000 || seen.has(cursor))throw new Error('Invalid or repeated registry cursor.');
    seen.add(cursor);
  }
  throw new Error('Registry traversal exceeded three pages.');
}
