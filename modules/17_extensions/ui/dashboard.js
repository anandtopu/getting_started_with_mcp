import { App } from "@modelcontextprotocol/ext-apps";

const app = new App({ name: "Lumen analytics", version: "1.0.0" });
const status = document.querySelector("#status");
const chart = document.querySelector("#chart");

function render(result) {
  const data = result.structuredContent;
  if (result.isError || !data || !Array.isArray(data.counts)) {
    status.textContent = "Could not read analytics. Try refreshing.";
    return;
  }
  chart.replaceChildren();
  for (const item of data.counts) {
    const row = document.createElement("li");
    // Treat all server data as text; never insert tool output as HTML.
    row.textContent = `${item.status}: ${item.count}`;
    chart.append(row);
  }
  status.textContent = `${data.total} synthetic work items. Read-only dashboard.`;
}

app.ontoolresult = render;
document.querySelector("#refresh").addEventListener("click", async () => {
  try {
    render(await app.callServerTool({ name: "analytics_dashboard", arguments: {} }));
  } catch {
    status.textContent = "Refresh failed. Check the host connection.";
  }
});
await app.connect();
