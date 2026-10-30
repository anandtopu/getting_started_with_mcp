import { test, expect } from '@playwright/test';

test('review, deny, task input/cancel, App refresh and browser sandbox', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('#status')).toHaveText('Workspace ready', {timeout:30000});
  await page.screenshot({path:'.runtime/phase7/chat-initial.png',fullPage:true});
  await page.getByRole('button',{name:/Save a follow-up note/}).click();
  await expect(page.getByRole('heading',{name:'Allow this tool call?'})).toBeVisible();
  await expect(page.locator('#decision')).toContainText('notes__create_note');
  await page.getByRole('button',{name:'Decline',exact:true}).click();
  await expect(page.locator('#status')).toHaveText('complete');
  await expect(page.locator('#conversation')).toContainText('Call declined');

  await page.getByRole('button',{name:/Draft a weekly update/}).click();
  await expect(page.locator('#decision')).toContainText('gateway__workflow__triage_week');
  await page.getByRole('button',{name:'Approve once'}).click();
  await expect(page.locator('#decision')).toContainText('gateway__workflow__draft_status');
  await page.getByRole('button',{name:'Approve once'}).click();
  await expect(page.locator('#status')).toHaveText('complete');
  await expect(page.locator('#conversation')).toContainText('Tool evidence');

  await page.getByRole('button',{name:/Build a quarterly report/}).click();
  await page.getByRole('button',{name:'Approve once'}).click();
  await page.getByLabel('include details').check();
  await page.getByRole('button',{name:'Submit input'}).click();
  await expect(page.locator('#status')).toHaveText('complete');
  await expect(page.locator('.task-state')).toContainText('completed');

  await page.getByRole('button',{name:/Build a quarterly report/}).click();
  await page.getByRole('button',{name:'Approve once'}).click();
  await expect(page.getByLabel('include details')).toBeVisible();
  await page.getByRole('button',{name:'Cancel operation'}).click();
  await expect(page.locator('#status')).toHaveText('cancelled');
  await expect(page.locator('.task-state')).toContainText('cancelled');

  await page.getByRole('button',{name:/Open analytics/}).click();
  await page.getByRole('button',{name:'Approve once'}).click();
  const view = page.frameLocator('#app-frame iframe');
  await expect(view.locator('#status')).toContainText('400 synthetic work items');
  await view.getByRole('button',{name:'Refresh counts'}).click();
  await expect(view.locator('#status')).toContainText('400 synthetic work items');
  await expect(page.locator('#app-frame iframe')).toHaveAttribute('sandbox','allow-scripts');
  const frame = page.frames().find(f=>f.url().includes('/api/app-view/'))!;
  expect(await frame.evaluate(() => { try { void window.parent.document.body; return false; } catch { return true; } })).toBe(true);
  expect(await frame.evaluate(async () => { try { await fetch('https://example.com/'); return false; } catch { return true; } })).toBe(true);
  await page.locator('#app-panel').scrollIntoViewIfNeeded();
  await page.screenshot({path:'.runtime/phase7/chat-app.png',fullPage:true});
  await page.getByRole('button',{name:'Close view'}).click();
  await expect(page.locator('#app-frame iframe')).toHaveCount(0);
  await page.getByRole('button',{name:'Reconnect',exact:true}).click();
  await expect(page.locator('#conversation')).toContainText('Reconnected.', { timeout: 30000 });
});

test('mobile layout and forged browser request rejection', async ({ page, request }) => {
  await page.setViewportSize({width:390,height:844}); await page.goto('/');
  await expect(page.locator('#status')).toHaveText('Workspace ready',{timeout:30000});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await page.screenshot({path:'.runtime/phase7/chat-mobile.png',fullPage:true});
  const response=await request.post('/api/session',{headers:{Origin:'https://evil.example','x-lumen-client':'web'},data:{}});
  expect(response.status()).toBe(403);
});
