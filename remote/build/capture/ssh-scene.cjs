// Captures a GUI scene after a real fit: shots/20-ssh.png with OFE-GUI started
// with -ssh (the GUI, its Terminal and the fit on the remote host; the data
// uploaded from this computer into the remote folder), or, with SHOT and
// SETTINGS=1, shots/30-connect.png with -connect-remote (GUI and Terminal on
// this computer, the fit on the remote host, Settings showing the field).
//   SHOT     the file name in shots/ (default 20-ssh.png)
//   TERM_CMDS  the Terminal commands, separated by |
//   GUI      the forwarded address -ssh opened (default http://127.0.0.1:8143/)
//   DATA     the data file to upload (ffc-relaxation.dat)
//   PROFILE  a fresh Chromium profile folder
//   CHROME   a Chromium binary, if Playwright has none of its own
const { chromium } = require('playwright-core');
const path = require('path');
const GUI = process.env.GUI || 'http://127.0.0.1:8143/';
const OUT = path.join(__dirname, '..', 'shots', process.env.SHOT || '20-ssh.png');

// [Settings |] Options | Terminal over Plots | Parameters over Output
// (SETTINGS=1 shows Settings, for -connect-remote's pre-filled field)
const SETTINGS = !!process.env.SETTINGS;
const LAYOUT = { version: 1, cols: [
  { w: SETTINGS ? 0.28 : 0.25, panes: [{ id: 'settings', h: 1, hidden: !SETTINGS }] },
  { w: 0.30, panes: [{ id: 'form', h: 1 }] },
  { w: 0.38, panes: [{ id: 'terminal', h: 1 }, { id: 'selected', auto: true }, { id: 'plots', h: 1.35 }] },
  { w: 0.32, panes: [{ id: 'fits', auto: true }, { id: 'parameters', auto: true }, { id: 'output', h: 1 }] },
] };

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

  await page.click('text=Function + data files').catch(() => {});
  await page.fill('#function', 'Mz(t,M0:1,Minf:0.05,T1:2[0.01<100])=Minf+(M0-Minf)*exp(-t/T1)');
  await page.dispatchEvent('#function', 'input');
  if (process.env.DATA) { await page.setInputFiles('#dataFilesPicker', process.env.DATA); await page.waitForTimeout(2000); }
  for (const id of ['#logX', '#reducedChi2']) if (!(await page.isChecked(id))) await page.check(id, { force: true });
  const autoY = await page.$('xpath=//label[normalize-space(.)="auto Y"]/input');
  if (autoY && !(await autoY.isChecked())) await autoY.check({ force: true });
  await page.fill('#fitMethods', 'simp scan min');
  await page.click('#runBtn');
  await page.waitForFunction(() => /done|error|fail/i.test(document.getElementById('status').textContent), null, { timeout: 180000 });
  await page.waitForTimeout(3000);
  console.log('status:', await page.textContent('#status'));

  await page.click('#terminalToggleBtn'); await page.waitForTimeout(2500);
  const term = await page.$('.xterm-helper-textarea');
  await term.focus();
  await page.keyboard.type('clear\n'); await page.waitForTimeout(800);
  for (const cmd of (process.env.TERM_CMDS || 'hostname; uname -m|pwd|ls').split('|')) {
    await page.keyboard.type(cmd + '\n'); await page.waitForTimeout(1200);
  }
  await page.keyboard.press('Alt+KeyH'); await page.waitForTimeout(300);
  await page.evaluate(() => { const b = [...document.querySelectorAll('button')].find(b => b.textContent.trim() === 'Plots'); b?.click(); });
  await page.waitForTimeout(2500);
  await page.mouse.move(5, 1075);
  await page.screenshot({ path: OUT });
  console.log('wrote', OUT);
  await ctx.close();
})();
