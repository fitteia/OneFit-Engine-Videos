const { chromium } = require('playwright-core');
const S = process.env.S;
(async () => {
  const ctx = await chromium.launchPersistentContext(S + '/vid/profile', { executablePath: process.env.CHROME, viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2, colorScheme: 'dark' });
  const page = ctx.pages()[0] || await ctx.newPage();
  page.on('dialog', d => d.accept().catch(() => {}));
  await page.goto('http://127.0.0.1:19143/report?job=035fb07734602bd91ce69b90dcb6710a&workFolder=/home/ofe/video-v2/work'); await page.waitForTimeout(4000);
  if (!(await page.isChecked('#roundOpt'))) { await page.check('#roundOpt'); await page.waitForTimeout(2000); }
  const h1 = page.locator('#paper h1').first();
  await h1.click(); await page.keyboard.press('Control+A'); await page.keyboard.type('Field-cycling NMR relaxation: T1 fit'); await page.waitForTimeout(500);
  const author = page.locator('#paper [data-placeholder="Author (optional)"]');
  if (await author.count()) { await author.first().click(); await page.keyboard.press('Control+A'); await page.keyboard.type('OneFit-Engine demo'); await page.waitForTimeout(300); }
  if (!(await page.locator('#paper .figure, #paper [data-figure]').count())) {
    await page.click('button.figures-add'); await page.waitForTimeout(2000);
    await page.screenshot({ path: `${S}/vid/shots/32-addfig.png` });
    await page.getByText('relaxation.agr', { exact: true }).click(); await page.waitForTimeout(500);
    await page.getByRole('button', { name: 'Pick files' }).click();
    await page.waitForTimeout(4000);
  }
  await page.click('#saveBtn'); await page.waitForTimeout(1500);
  await page.mouse.move(5, 1075);
  await page.screenshot({ path: `${S}/vid/shots/30-report.png` });
  await page.screenshot({ path: `${S}/vid/shots/31-report-full.png`, fullPage: true });
  const paper = await page.$('#paper'); await paper.screenshot({ path: `${S}/vid/shots/33-report-paper.png` });
  console.log((await page.evaluate(() => document.querySelector('#paper').innerText)).slice(-900));
  await ctx.close();
})();
