/** Framework integration pages exercise. See README for boundary cases. */
export function solve(cursors:(string|undefined)[]):number { const seen=new Set<string>();for(let i=0;i<cursors.length && i<20;i++){const cursor=cursors[i];if(cursor===undefined)return i+1;if(seen.has(cursor))throw new Error('Repeated cursor');seen.add(cursor);}throw new Error('Page budget exceeded'); }
