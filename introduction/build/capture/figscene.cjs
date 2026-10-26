const { chromium } = require('playwright-core');
const S = process.env.S;
(async () => {
  const ctx = await chromium.launchPersistentContext(S + '/vid/profile', { executablePath: process.env.CHROME, viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2, colorScheme: 'dark' });
  const page = ctx.pages()[0] || await ctx.newPage();
  page.on('dialog', d => d.accept().catch(() => {}));
  await page.goto('http://127.0.0.1:19143/figures?workFolder=/home/ofe/video-v2/work'); await page.waitForTimeout(2000);
  const opts = await page.$$eval('#figureSelect option', o => o.map(x => x.value));
  console.log('figures:', opts);
  if (!opts.some(v => v.includes('relaxation'))) {
    await page.click('#newBtn'); await page.waitForTimeout(800);
    await page.fill('#dlgName', 'relaxation');
    await page.fill('#dlgAgr', '/home/ofe/video-v2/work/ofe-tmp/fit-curves-1.agr');
    await page.locator('#dlgAgr').blur(); await page.waitForTimeout(1500);
    await page.click('#dlgOk'); await page.waitForTimeout(3000);
  }
  else { await page.selectOption('#figureSelect', 'relaxation'); await page.waitForTimeout(2500); }
  await page.screenshot({ path: `${S}/vid/shots/20-fig-new.png` });
  const edit = async (part, label, value) => {
    await page.click(`#parts [data-id="${part}"]`); await page.waitForTimeout(700);
    const ta = page.locator('#props label', { hasText: label }).locator('textarea').first();
    await ta.fill(value); await ta.blur(); await page.waitForTimeout(2500);
  };
  await edit('g0', 'Title', 'Field-cycling NMR relaxation');
  await edit('g0', 'Subtitle', 'T005F1 at 3.0 kHz: fitted T\\s1\\N = 2.00');
  await edit('g0.x', 'Label', 'Evolution time \\xt');
  await edit('g0.y', 'Label', 'M\\sz\\N (normalized)');
  await page.click('#parts [data-id="g0"]'); await page.waitForTimeout(1500);
  await page.mouse.move(5, 1075);
  await page.screenshot({ path: `${S}/vid/shots/21-fig-edited.png` });
  await page.keyboard.press('Escape'); await page.mouse.click(1800, 1000); await page.waitForTimeout(800); await page.mouse.move(5,1075);
  await page.screenshot({ path: `${S}/vid/shots/22-fig-clean.png` });
  await ctx.close();
})();
