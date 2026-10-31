import { defineConfig } from '@playwright/test';
import shared from './playwright.config.ts';
export default defineConfig({ ...shared, use: { ...shared.use, baseURL: 'http://127.0.0.1:8768' }, outputDir: '.runtime/browser-typescript-results', webServer: { command: 'node --import tsx scripts/typescript_chat.ts', url: 'http://127.0.0.1:8768', reuseExistingServer: false, timeout: 60000 } });
