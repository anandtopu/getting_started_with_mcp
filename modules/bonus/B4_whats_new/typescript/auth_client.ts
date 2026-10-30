/** Stdin contains ephemeral fixture credentials; stdout contains only the public outcome. */
import { machineDemo } from '../../../../common/typescript/machine_auth.ts';
const chunks:Buffer[]=[];let size=0;
for await(const chunk of process.stdin){size+=chunk.length;if(size>16000)throw new Error('Fixture input too large');chunks.push(chunk);}
console.log(JSON.stringify(await machineDemo(JSON.parse(Buffer.concat(chunks).toString()))));
