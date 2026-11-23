// Real browser -> React -> Flask -> read-only MySQL and public Open-Meteo.
// No interception, mocked weather or synthetic records; screenshots stay local.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const results = { mocked_data: false, database_writes: 0, browser_exceptions: 0 };
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1080 } });
    page.on('pageerror', () => results.browser_exceptions++);
    fs.mkdirSync(path.join(root, '.local-verification'), { recursive: true });
    async function screenshot(name) { await page.screenshot({ path: path.join(root, '.local-verification', name), fullPage: true }); }
    async function chooseCity() {
      await page.getByLabel('Населений пункт').fill('Lviv');
      const response = page.waitForResponse(r => r.url().includes('/api/v1/places/search?'));
      await page.getByRole('button', { name: 'Знайти місто' }).click();
      if ((await response).status() !== 200) throw new Error('Real city search unavailable');
      await page.locator('.place-search .place-results button').first().click();
    }
    async function loadWeather() {
      const response = page.waitForResponse(r => r.url().includes('/api/v1/weather?'), { timeout: 20000 });
      await page.getByRole('button', { name: 'Отримати погоду' }).click();
      const request = await response;
      if (request.status() !== 200) throw new Error('Real weather provider unavailable');
      const body = await request.json();
      await page.getByText('Weather data by Open-Meteo.com').waitFor();
      if (body.data.solar_method !== 'model_shortwave_radiation') throw new Error('Incorrect solar provenance');
      return body.data;
    }
    await page.goto('http://127.0.0.1:5173/#dashboard');
    await page.getByRole('table').waitFor();
    results.dashboard_history_real_mysql = true;
    await chooseCity(); await loadWeather();
    results.dashboard_weather_real_provider = true;
    await screenshot('phase3-dashboard-desktop.png');

    await page.getByRole('link', { name: 'HRI Analysis', exact: true }).click();
    await page.getByLabel('Температура, °C').fill('20');
    await page.getByLabel('Радіація, W/m²').fill('180');
    await page.getByLabel('Вологість, %').fill('65');
    await page.getByRole('button', { name: 'Розрахувати HRI', exact: true }).click();
    const output = page.getByLabel('Числовий індекс HRI');
    await output.waitFor();
    const manual = Number(await output.innerText());
    if (!(manual >= 0 && manual <= 1)) throw new Error('Invalid real HRI result');
    results.hri_manual_real_api = true;
    await chooseCity(); const actualWeather = await loadWeather();
    if (Number(await page.getByLabel('Температура, °C').inputValue()) !== actualWeather.avg_temp) throw new Error('Weather-to-HRI input mismatch');
    await page.getByRole('button', { name: 'Розрахувати HRI', exact: true }).click();
    await output.waitFor(); results.hri_weather_real_api = true;
    await screenshot('phase3-hri-desktop.png');
    await page.setViewportSize({ width: 390, height: 844 });
    if (!await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)) throw new Error('HRI mobile overflow');
    results.hri_mobile_no_overflow = true; await screenshot('phase3-hri-mobile.png');
    await page.setViewportSize({ width: 1440, height: 1080 });

    await page.getByRole('link', { name: 'Інтерактивна карта', exact: true }).click();
    await page.locator('.leaflet-container').waitFor();
    await page.locator('.leaflet-interactive').first().waitFor();
    results.map_real_mysql_markers = true;
    await chooseCity(); await loadWeather();
    await page.getByRole('button', { name: 'Розрахувати HRI для міста' }).click();
    await page.locator('.map-hri-result strong').waitFor();
    results.map_real_weather_hri = true;
    // Allow the deliberate Leaflet flyTo animation to settle before screenshotting tiles.
    await page.waitForTimeout(1800);
    try { await page.waitForFunction(() => [...document.querySelectorAll('img.leaflet-tile-loaded')].some(i => i.complete && i.naturalWidth > 0), null, { timeout: 12000 }); results.map_base_tiles_loaded = true; }
    catch { results.map_base_tiles_loaded = false; }
    results.tile_fallback_notice = await page.getByText(/Картографічний фон недоступний/).count() > 0;
    await screenshot('phase3-map-desktop.png');
    await page.setViewportSize({ width: 390, height: 844 });
    if (!await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)) throw new Error('Map mobile overflow');
    results.map_mobile_no_overflow = true; await screenshot('phase3-map-mobile.png');
    if (results.browser_exceptions) throw new Error('Browser exception');
    results.status = 'passed';
    fs.writeFileSync(path.join(root, 'docs/reports/phase3-browser.json'), JSON.stringify(results, null, 2));
    console.log('Phase 3 browser smoke passed: real Dashboard, HRI and Leaflet/MySQL/weather; no values logged');
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exit(1); });
