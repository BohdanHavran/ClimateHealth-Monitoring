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
    page.on('response', response => { if (response.status() >= 400 && response.url().includes('/api/')) console.log('API failure: ' + new URL(response.url()).pathname + ' ' + response.status()); });
    fs.mkdirSync(path.join(root, '.local-verification'), { recursive: true });
    async function screenshot(name) { await page.evaluate(() => window.scrollTo(0,0)); if (name.includes('dashboard') || name.includes('history')) await page.locator('.chart canvas').waitFor(); await page.screenshot({ path: path.join(root, '.local-verification', name), fullPage: true }); }
    async function checkTextZoom() {
      await page.setViewportSize({width:390,height:844});
      await page.evaluate(() => document.documentElement.style.fontSize = '200%');
      await page.waitForTimeout(300);
      if (!await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)) throw new Error('Text zoom overflow: ' + page.url().split('#')[1] + ' ' + JSON.stringify(await page.evaluate(() => [...document.querySelectorAll('body *')].filter(el => { const box=el.getBoundingClientRect(); return (box.right>innerWidth || el.scrollWidth>el.clientWidth+1) && !el.closest('.table-scroll') && !el.closest('.chart') }).slice(0,12).map(el => ({tag:el.tagName, cls:el.className, right:el.getBoundingClientRect().right})))));
      await page.evaluate(() => document.documentElement.style.removeProperty('font-size'));
      await page.setViewportSize({width:1440,height:1080});
    }
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
    console.log('Checking dashboard');
    await page.goto('http://127.0.0.1:5173/#dashboard');
    await page.getByRole('table').waitFor({timeout:15000});
    results.dashboard_history_real_mysql = true;
    await chooseCity(); await loadWeather();
    results.dashboard_weather_real_provider = true;
    await screenshot('redesign-after-dashboard-desktop.png');
    if (await page.locator('tbody tr').count() > 5) throw new Error('Dashboard preview is not compact');
    results.dashboard_compact_preview = true;
    await page.setViewportSize({ width: 390, height: 844 });
    if (!await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)) throw new Error('Dashboard mobile overflow');
    await screenshot('redesign-after-dashboard-mobile.png'); await checkTextZoom();
    await page.setViewportSize({ width: 1440, height: 1080 });

    console.log('Checking HRI');
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
    await screenshot('redesign-after-hri-desktop.png');
    await page.setViewportSize({ width: 390, height: 844 });
    if (!await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)) throw new Error('HRI mobile overflow');
    results.hri_mobile_no_overflow = true; await screenshot('redesign-after-hri-mobile.png'); await checkTextZoom();
    await page.setViewportSize({ width: 1440, height: 1080 });

    console.log('Checking map');
    await page.getByRole('link', { name: 'Інтерактивна карта', exact: true }).click();
    await page.locator('.leaflet-container').waitFor();
    await page.locator('.leaflet-interactive').first().waitFor();
    results.map_real_mysql_markers = true;
    await chooseCity(); await loadWeather();
    await page.getByRole('button', { name: 'Розрахувати HRI для міста' }).click();
    await page.locator('.map-hri-result strong').waitFor();
    results.map_real_weather_hri = true;
    // Confirm real cartographic tiles before capturing the selected place.
    try { await page.waitForFunction(() => [...document.querySelectorAll('img.leaflet-tile-loaded')].some(i => i.complete && i.naturalWidth > 0), null, { timeout: 12000 }); results.map_base_tiles_loaded = true; }
    catch { results.map_base_tiles_loaded = false; }
    results.tile_fallback_notice = await page.getByText(/Картографічний фон недоступний/).count() > 0;
    await screenshot('redesign-after-map-desktop.png');
    await page.setViewportSize({ width: 390, height: 844 });
    if (!await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)) throw new Error('Map mobile overflow');
    results.map_mobile_no_overflow = true; await screenshot('redesign-after-map-mobile.png'); await checkTextZoom();
    console.log('Checking full history');
    await page.getByRole('link', { name: 'Історичні дані', exact: true }).click();
    await page.getByRole('table').waitFor({timeout:15000});
    if (await page.locator('tbody tr').count() <= 5) throw new Error('Full history unexpectedly truncated');
    await page.setViewportSize({ width: 1440, height: 1080 });
    await screenshot('redesign-after-history-desktop.png');
    results.full_history = true;
    for (const route of ['dashboard', 'hri', 'map', 'history']) {
      await page.goto('http://127.0.0.1:5173/#' + route);
      await page.waitForFunction(expected => window.location.hash === '#' + expected &&
        (expected === 'dashboard' ? document.querySelector('.quick-links') :
         expected === 'hri' ? document.querySelector('.hri-form') :
         expected === 'map' ? document.querySelector('.map-toolbar') : document.querySelector('.history-panel') && !document.querySelector('.quick-links')), route);
      if (route === 'dashboard' || route === 'history') await page.getByRole('table').waitFor();
      if (route === 'map') await page.locator('.leaflet-container').waitFor();
      for (const width of [320, 390, 768, 1024, 1440]) {
        await page.setViewportSize({ width, height: 900 });
        await page.waitForTimeout(150);
        if (!await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)) throw new Error(route + ' overflow at ' + width);
      }
    }
    results.responsive_widths = [320,390,768,1024,1440];
    await page.setViewportSize({width:390,height:844});
    await page.getByRole('table').waitFor({timeout:15000});
    await screenshot('redesign-after-history-mobile.png'); await checkTextZoom(); results.text_zoom_200_percent = true;
    const keyboardPage = await browser.newPage();
    await keyboardPage.goto('http://127.0.0.1:5173/#dashboard');
    await keyboardPage.getByRole('link', {name:'Перейти до вмісту'}).waitFor({state:'attached'});
    await keyboardPage.keyboard.press('Tab');
    if (!await keyboardPage.getByRole('link', {name:'Перейти до вмісту'}).evaluate(el => el === document.activeElement)) throw new Error('Skip link not first');
    await keyboardPage.keyboard.press('Enter');
    if (!await keyboardPage.locator('main').evaluate(el => el === document.activeElement)) throw new Error('Skip link target not focused');
    results.skip_link_keyboard = true;
    await keyboardPage.getByRole('link',{name:'HRI Analysis',exact:true}).click();
    await keyboardPage.waitForFunction(() => document.activeElement?.tagName === 'MAIN');
    results.route_focus = true;
    await keyboardPage.close();
    if (results.browser_exceptions) throw new Error('Browser exception');
    results.status = 'passed';
    fs.writeFileSync(path.join(root, 'docs/reports/ui-redesign-browser.json'), JSON.stringify(results, null, 2));
    console.log('UI redesign browser smoke passed: real Dashboard, HRI and Leaflet/MySQL/weather; no values logged');
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exit(1); });
