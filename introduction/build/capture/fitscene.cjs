const { chromium } = require('playwright-core');
const S = process.env.S;
(async () => {
  const ctx = await chromium.launchPersistentContext(S + '/vid/profile', { executablePath: process.env.CHROME, viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2, colorScheme: 'dark' });
  const browser = ctx;
  const page = ctx.pages()[0] || await ctx.newPage();
  page.on('dialog', d => d.accept().catch(() => {}));
  await page.goto('http://127.0.0.1:19143/'); await page.waitForTimeout(2000);
  await page.keyboard.press('Escape');
  if (!(await page.isVisible('#terminalToggleBtn'))) { await page.click('text=Compact layout...'); await page.waitForTimeout(1200); await page.keyboard.press('Escape'); }
  const label = await page.evaluate(() => document.querySelector('#terminalToggleBtn')?.textContent.trim());
  console.log('terminal btn:', label);
  await page.click('#terminalToggleBtn'); await page.waitForTimeout(2500);
  const term = await page.$('.xterm-helper-textarea');
  if (term) {
    await term.focus();
    await page.keyboard.type('export PATH=/opt/onefite-go/bin:$PATH; clear\n'); await page.waitForTimeout(800);
    await page.keyboard.type('onefite --version\n'); await page.waitForTimeout(1500);
    await page.keyboard.type('ls ofe-tmp/*.pdf ofe-tmp/*.json\n'); await page.waitForTimeout(1200);
    await page.keyboard.press('Alt+KeyH'); await page.waitForTimeout(300);
  } else console.log('no terminal');
  await page.evaluate(() => { const b = [...document.querySelectorAll('button')].find(b => b.textContent.trim() === 'Plots'); b?.click(); });
  await page.waitForTimeout(1500);
  await page.mouse.move(5, 1075);
  await page.screenshot({ path: `${S}/vid/shots/10-fit-compact.png` });
  await browser.close();
})();
