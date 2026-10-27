// Captures the GUI scenes of the fits video from a real OFE-GUI session, in
// order, into shots/:
//   10-model.png  Function + data files: the model and the Stelar file
//                 (44 relaxation curves), fitted Individual
//   20-json.png   JSON/SAV/Jobs: the saved t005.json, its fields in the
//                 JSON viewer
//   30-jobs.png   the Jobs table: three fits, each with its own mode
//   21-json-tags.png  the same, scrolled to SelectedDataSet, T and Tags
//   40-batch.png  the batch done: the Fits bar, the Batch output
//   41-batch-global.png  the global fit picked in the Fits bar
// SCENES picks some (e.g. "30,40"); later scenes expect the earlier ones'
// files (t005.json, fits.txt) in the GUI's folder.
//   GUI      the GUI's address (default http://127.0.0.1:8143/)
//   DATA     the data file to upload (T005F1_1.sdf)
//   DIR      the GUI's folder on its machine (/home/ofe/video3)
//   PROFILE  a fresh Chromium profile folder
//   CHROME   a Chromium binary, if Playwright has none of its own
const { chromium } = require('playwright-core');
const path = require('path');
const GUI = process.env.GUI || 'http://127.0.0.1:8143/';
const DIR = process.env.DIR || '/home/ofe/video3';
const SCENES = (process.env.SCENES || '10,20,30,40').split(',');
const shot = name => path.join(__dirname, '..', 'shots', name);
const MODEL = 'Mz(t,M0:1,Minf:0.05,T1:2[0.01<100])=Minf+(M0-Minf)*exp(-t/T1)';
const STRETCHED = 'Mz(t,M0:1,Minf:0.05,T1:2[0.01<100],b:0.9[0.3<1])=Minf+(M0-Minf)*exp(-pow(t/T1,b))';

// Options | Terminal over Plots | Fits, Parameters over Output
const LAYOUT = { version: 1, cols: [
  { w: 0.25, panes: [{ id: 'settings', h: 1, hidden: true }] },
  { w: 0.30, panes: [{ id: 'form', h: 1 }] },
  { w: 0.38, panes: [{ id: 'terminal', h: 0.55 }, { id: 'selected', auto: true }, { id: 'plots', h: 1.35 }] },
  { w: 0.32, panes: [{ id: 'fits', auto: true }, { id: 'parameters', auto: true }, { id: 'output', h: 1 }] },
] };

async function fitAndWait(page) {
  await page.click('#runBtn');
  await page.waitForTimeout(1500);
  await page.waitForFunction(() => /done|error|fail/i.test(document.getElementById('status').textContent), null, { timeout: 300000 });
  await page.waitForTimeout(3000);
  console.log('status:', await page.textContent('#status'));
}
async function terminal(page, cmds) {
  const term = await page.$('.xterm-helper-textarea');
  await term.focus();
  await page.keyboard.type('clear\n'); await page.waitForTimeout(800);
  for (const cmd of cmds) { await page.keyboard.type(cmd + '\n'); await page.waitForTimeout(1200); }
  await page.keyboard.press('Alt+KeyH'); await page.waitForTimeout(300);
}
async function check(page, sel, on) {
  if ((await page.isChecked(sel)) !== on) await page.setChecked(sel, on, { force: true });
}

(async () => {
  const ctx = await chromium.launchPersistentContext(process.env.PROFILE || path.join(__dirname, 'profile'), {
    ...(process.env.CHROME ? { executablePath: process.env.CHROME } : {}),
    viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2, colorScheme: 'dark',
  });
  await ctx.addInitScript((layout) => {
    try {
      localStorage.setItem('onefite-gui-theme', 'dark');
      localStorage.setItem('onefite-gui-layout-mode', 'compact');
      localStorage.setItem('onefite-gui-panes-v1', JSON.stringify(layout));
    } catch (e) {}
  }, LAYOUT);
  const page = ctx.pages()[0] || await ctx.newPage();
  page.on('dialog', d => d.accept().catch(() => {}));
  await page.goto(GUI); await page.waitForTimeout(2500);
  await page.keyboard.press('Escape');
  await page.click('#terminalToggleBtn'); await page.waitForTimeout(2000);

  if (SCENES.includes('10')) {
    await page.click('#tabFunction');
    await page.fill('#function', MODEL);
    await page.dispatchEvent('#function', 'input');
    await page.setInputFiles('#dataFilesPicker', process.env.DATA || 'T005F1_1.sdf'); await page.waitForTimeout(2000);
    await page.selectOption('#fitMode', 'individual');
    for (const id of ['#logX', '#reducedChi2', '#autoY']) await check(page, id, true);
    await check(page, '#mp4', false);
    await page.fill('#fitMethods', 'simp scan min');
    await page.fill('#saveTo', 't005.json');
    await fitAndWait(page);
    await terminal(page, ['nproc', 'cp ofe-tmp/t005.json .', 'grep -o "# DATA" t005.json | wc -l']);
    await page.mouse.move(5, 1075);
    await page.screenshot({ path: shot('10-model.png') });
    console.log('wrote 10-model.png');
  }
  if (SCENES.includes('20')) {
    await page.click('#tabInputFile');
    await page.evaluate(p => setInputFiles([p]), DIR + '/t005.json'); await page.waitForTimeout(1500);
    await page.selectOption('#fitMode', 'auto');
    await page.evaluate(p => openJsonBrowser(p, true), DIR + '/t005.json'); await page.waitForTimeout(1500);
    await page.mouse.move(5, 1075);
    await page.screenshot({ path: shot('20-json.png') });
    console.log('wrote 20-json.png');
    await page.evaluate(() => { const t = document.getElementById('jsonFields'); const r = [...t.querySelectorAll('tr')].find(r => /^\s*SelectedDataSet/.test(r.textContent)); r && r.scrollIntoView({ block: 'start' }); });
    await page.waitForTimeout(800);
    await page.screenshot({ path: shot('21-json-tags.png') });
    console.log('wrote 21-json-tags.png');
    await page.keyboard.press('Escape'); await page.waitForTimeout(500);
    await page.evaluate(() => document.getElementById('jsonModal').classList.remove('open'));
  }

  if (SCENES.includes('30')) {
    await page.click('#tabFunction');
    await page.fill('#function', MODEL + '\n' + STRETCHED);
    await page.dispatchEvent('#function', 'input');
    await page.click('#fitsListFromFormBtn'); await page.waitForTimeout(1000);
    const rows = page.locator('#fitsListTable tbody tr');
    for (let i = 0; i < await rows.count(); i++) await rows.nth(i).locator('select').selectOption('individual');
    await page.click('#fitsListAdd');
    const last = rows.nth((await rows.count()) - 1);
    await last.locator('input[type=text]').first().fill(DIR + '/t005.json');
    await last.locator('select').selectOption('global');
    await page.click('#fitsListMaximize'); await page.waitForTimeout(800);
    await page.mouse.move(5, 1075);
    await page.screenshot({ path: shot('30-jobs.png') });
    console.log('wrote 30-jobs.png');
    await page.click('#fitsListUse'); await page.waitForTimeout(1500);
  }

  if (SCENES.includes('40')) {
    await page.fill('#jobs', '2');
    await fitAndWait(page);
    await terminal(page, ['ls', 'ls batch-*']);
    await page.mouse.move(5, 1075);
    await page.screenshot({ path: shot('40-batch.png') });
    console.log('wrote 40-batch.png');
    await page.locator('#batchFits button', { hasText: 't005-global' }).first().click(); await page.waitForTimeout(3000);
    await page.mouse.move(5, 1075);
    await page.screenshot({ path: shot('41-batch-global.png') });
    console.log('wrote 41-batch-global.png');
  }
  await ctx.close();
})();
