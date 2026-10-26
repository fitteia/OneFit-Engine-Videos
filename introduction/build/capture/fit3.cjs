const { chromium } = require('playwright-core');
const S = process.env.S;
(async () => {
  const ctx = await chromium.launchPersistentContext(S + '/vid/profile', { executablePath: process.env.CHROME, viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2, colorScheme: 'dark' });
  const page = ctx.pages()[0] || await ctx.newPage();
  page.on('dialog', d => { console.log('dialog:', d.message()); d.accept().catch(() => {}); });
  await page.goto('http://127.0.0.1:19143/'); await page.waitForTimeout(2000);
  await page.keyboard.press('Escape');
  await page.fill('#fitMethods', 'simp scan min');
  await page.click('#runBtn');
  await page.waitForFunction(() => /done|error|fail/i.test(document.getElementById('status').textContent), null, { timeout: 120000 });
  await page.waitForTimeout(3000);
  console.log('status:', await page.textContent('#status'));
  await ctx.close();
})();
