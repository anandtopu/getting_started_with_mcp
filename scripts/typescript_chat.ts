/** Run the native Chat Pro application; all model keys stay in this process. */
import { chatPro } from '../common/typescript/chat_pro.ts';
import { hostConfig } from '../common/typescript/chat_services.ts';
const value = (flag: string) => { const index = process.argv.indexOf(flag); return index < 0 ? undefined : process.argv[index + 1]; };
try { process.loadEnvFile(); } catch { /* .env is optional. */ }
const port = Number(value('--port') ?? 8768);
const app = await chatPro(port, hostConfig(value('--config')));
console.log(`Lumen Chat Pro: http://127.0.0.1:${port}`);
for (const event of ['SIGTERM', 'SIGINT'] as const) process.once(event, () => { void app.close(); });
