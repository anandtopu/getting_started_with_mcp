/** Environment and first contact review exercise. See README for boundary cases. */
export function solve(reviewed:string, current:string, approved:boolean):boolean { return approved && reviewed.length>0 && reviewed===current; }
