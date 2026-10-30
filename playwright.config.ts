import { defineConfig } from '@playwright/test';
export default defineConfig({testDir:'tests/browser',testMatch:'**/*.pw.ts',workers:1,timeout:90000,
  use:{baseURL:'http://127.0.0.1:8766',viewport:{width:1440,height:1000},headless:true},
  outputDir:'.runtime/browser-results',reporter:'line',
  webServer:{command:'uv run --frozen --all-extras python -m common.web_chat --port 8766',
    url:'http://127.0.0.1:8766',reuseExistingServer:false,timeout:60000},});
