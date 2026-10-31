/** Entrypoint for the native OAuth gateway container. */
import { oauthGateway } from '../common/typescript/gateway_http.ts';
const app = await oauthGateway({ issuer: process.env.LUMEN_ISSUER ?? 'http://127.0.0.1:8080/realms/lumen', resource: process.env.LUMEN_RESOURCE ?? 'http://127.0.0.1:8001/mcp', jwksUrl: process.env.LUMEN_JWKS_URL ?? 'http://127.0.0.1:8080/realms/lumen/protocol/openid-connect/certs', port: Number(process.env.PORT ?? 8000), bind: process.env.LUMEN_BIND ?? '127.0.0.1', upstreamMode: 'stdio' });
for (const event of ['SIGTERM', 'SIGINT'] as const) process.once(event, () => { void app.close(); });
