/** Bundle the official App bridge locally: node scripts/build_dashboard.mjs. */
import { build } from "esbuild";
import { writeFile } from "node:fs/promises";

const result = await build({
  entryPoints: ["modules/17_extensions/ui/dashboard.js"],
  bundle: true, minify: true, format: "esm", write: false, target: "es2022",
});
const script = result.outputFiles[0].text.replaceAll("</script", "<\\/script");
const html = `<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lumen analytics</title><style>
body{font:16px system-ui;padding:24px;color:#172b39;background:#f3f7f8}
button{padding:10px 18px;background:#136b66;color:white;border:0;border-radius:6px}
li{padding:10px;border-bottom:1px solid #ccd8df}h1{font-size:24px}
</style><h1>Lumen workspace</h1><p id="status" role="status">Waiting for tool data…</p>
<ul id="chart"></ul><button id="refresh" type="button">Refresh counts</button>
<script type="module">${script}</script></html>`;
await writeFile("modules/17_extensions/ui/dashboard.html", html);
console.log("Built self-contained MCP App with the official bridge.");
