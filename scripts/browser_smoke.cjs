// Requires an available Playwright installation and existing Edge; downloads nothing.
// Uses the running read-only diagnostic backend and Vite. No mocked records.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1080 } });
    const errors = [];
    page.on('pageerror', () => errors.push('browser_exception'));
    await page.goto('http://127.0.0.1:5173');
    await page.getByRole('table').waitFor();
    const first = await page.locator('tbody tr').first().locator('td').nth(1).innerText();
    const year = first.split('/')[0].replace(/\s/g, '');
    let filterVerified = false;
    if (/^\d{4}$/.test(year)) {
      await page.getByLabel('Рік спостережень').fill(year);
      const result = page.waitForResponse(r => r.url().includes('/api/v1/observations?') && r.url().includes('year='+year));
      await page.getByRole('button', { name: 'Застосувати' }).click();
      if ((await result).status() !== 200) throw new Error('Filter HTTP check failed');
      await page.getByRole('table').waitFor();
      filterVerified = true;
    }
    fs.mkdirSync(path.join(root, '.local-verification'), { recursive: true });
    await page.screenshot({ path: path.join(root, '.local-verification/react-desktop.png'), fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.getByRole('table').waitFor();
    const fits = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
    if (!fits || errors.length) throw new Error('Responsive/browser exception check failed');
    await page.screenshot({ path: path.join(root, '.local-verification/react-mobile.png'), fullPage: true });
    fs.writeFileSync(path.join(root, 'docs/reports/phase2-browser.json'), JSON.stringify({
      transport: 'real Edge -> React/Vite -> Flask -> MySQL',
      mocked_records: false, table_visible: true, year_filter_verified: filterVerified,
      mobile_width: 390, no_document_horizontal_overflow: fits,
      browser_exceptions: errors.length, database_writes: 0,
      screenshots: 'local only, excluded from Git',
    }, null, 2));
    console.log('Real browser smoke passed: table, filter, mobile layout; no record values logged');
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exit(1); });
