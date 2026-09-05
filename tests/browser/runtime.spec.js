const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');
const { test, expect } = require('@playwright/test');

const skillRoot = path.resolve(__dirname, '../..');
const builder = path.join(skillRoot, 'scripts', 'build_presentation.py');
const python = process.env.PYTHON || 'python';
let tempDir;
let deckUrl;
let remoteDeckUrl;

function fileUrl(file) {
  return 'file:///' + path.resolve(file).replace(/\\/g, '/');
}

function build(spec, output) {
  const result = spawnSync(python, [builder, spec, '--out', output], { encoding: 'utf8' });
  if (result.status !== 0) throw new Error(result.stderr || result.stdout);
}

test.beforeAll(() => {
  tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'html-deck-runtime-'));
  const output = path.join(tempDir, 'demo.html');
  build(path.join(skillRoot, 'examples', 'demo-deck.json'), output);
  deckUrl = fileUrl(output);

  const remoteSpec = {
    meta: { title: 'Remote embed state', language: 'en', theme: 'signal-noir', aspectRatio: '16:9' },
    slides: [{
      id: 'remote',
      content: '<div class="web-embed" data-network-required="true"><iframe src="https://example.invalid/demo" title="Remote demo"></iframe><p class="embed-fallback">A network connection is required; open the source page directly if embedding is blocked.</p></div>'
    }]
  };
  const remoteSpecPath = path.join(tempDir, 'remote.json');
  fs.writeFileSync(remoteSpecPath, JSON.stringify(remoteSpec), 'utf8');
  const remoteOutput = path.join(tempDir, 'remote.html');
  build(remoteSpecPath, remoteOutput);
  remoteDeckUrl = fileUrl(remoteOutput);
});

test.afterAll(() => {
  fs.rmSync(tempDir, { recursive: true, force: true });
});

test('desktop navigation renders charts and stays offline', async ({ page }) => {
  const requests = [];
  const errors = [];
  page.on('request', request => {
    if (/^https?:/i.test(request.url())) requests.push(request.url());
  });
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {
    if (message.type() === 'error') errors.push(message.text());
  });
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(deckUrl);
  await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
  await page.evaluate(() => window.__DECK_DEBUG__.goTo(1));
  await expect(page.locator('#deck-counter')).toHaveText('2 / 7');
  await page.waitForTimeout(800);
  await page.evaluate(() => window.__DECK_DEBUG__.goTo(2));
  await expect(page.locator('.slide.is-active .chart.is-ready')).toHaveCount(1);
  const pixels = await page.locator('.slide.is-active .chart canvas').evaluate(canvas => canvas.toDataURL().length);
  expect(pixels).toBeGreaterThan(10000);
  await page.waitForTimeout(800);
  await page.keyboard.press('End');
  await expect(page.locator('#deck-counter')).toHaveText('7 / 7');
  expect(requests).toEqual([]);
  expect(errors).toEqual([]);
});

test('deactivation stops count-up, disposes charts, and timeline re-entry is current', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto(deckUrl);
  await page.evaluate(() => window.__DECK_DEBUG__.goTo(1));
  await page.waitForTimeout(80);
  await page.evaluate(() => window.__DECK_DEBUG__.goTo(2));
  await expect(page.locator('#deck-counter')).toHaveText('3 / 7');
  const hiddenCounter = page.locator('#slide-metrics .count-up').first();
  const stoppedValue = await hiddenCounter.textContent();
  await page.waitForTimeout(450);
  expect(await hiddenCounter.textContent()).toBe(stoppedValue);

  const chart = page.locator('#slide-trend .chart');
  await expect(chart).toHaveClass(/is-ready/);
  expect(await chart.evaluate(element => Boolean(echarts.getInstanceByDom(element)))).toBe(true);
  await page.evaluate(() => window.__DECK_DEBUG__.goTo(3));
  await expect(page.locator('#deck-counter')).toHaveText('4 / 7');
  expect(await chart.evaluate(element => Boolean(echarts.getInstanceByDom(element)))).toBe(false);
  await page.evaluate(() => window.__DECK_DEBUG__.goTo(2));
  await expect(page.locator('#deck-counter')).toHaveText('3 / 7');
  await expect(chart).toHaveClass(/is-ready/);
  expect(await chart.evaluate(element => Boolean(echarts.getInstanceByDom(element)))).toBe(true);

  await page.evaluate(() => window.__DECK_DEBUG__.goTo(3));
  await page.evaluate(() => window.__DECK_DEBUG__.goTo(6));
  await page.evaluate(() => window.__DECK_DEBUG__.goTo(3));
  const timeline = page.locator('.slide.is-active .timeline');
  await timeline.locator('.timeline-item').last().click();
  await page.waitForTimeout(2100);
  await expect(timeline.locator('.timeline-item').last()).toHaveClass(/is-active/);
});

test('mobile reduced-motion framing and shared fallback remain usable', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto(deckUrl);
  await page.keyboard.press('End');
  await expect(page.locator('#deck-counter')).toHaveText('7 / 7');
  const controls = await page.locator('#controls').boundingBox();
  expect(controls.x).toBeGreaterThanOrEqual(0);
  expect(controls.x + controls.width).toBeLessThanOrEqual(390);

  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.addInitScript(() => {
    Object.defineProperty(document, 'startViewTransition', { value: undefined, configurable: true });
  });
  await page.goto(deckUrl);
  await page.evaluate(() => window.__DECK_DEBUG__.goTo(1));
  await page.waitForTimeout(80);
  expect(await page.locator('#shared-overlay .shared-clone').count()).toBeGreaterThan(0);
});

for (const mode of ['native', 'fallback']) {
  test(`backward navigation restores opening geometry with ${mode} transitions`, async ({ page }) => {
    if (mode === 'fallback') {
      await page.addInitScript(() => {
        Object.defineProperty(document, 'startViewTransition', { value: undefined, configurable: true });
      });
    }
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(deckUrl);
    await page.waitForTimeout(800);
    const opening = page.locator('#slide-opening');
    const signal = opening.locator('.signal-mark');
    const stage = page.locator('#deck-stage');
    await page.evaluate(() => {
      const slide = document.querySelector('#slide-opening');
      window.__DECK_DEBUG__.setFragmentState(slide, slide.querySelectorAll('.fragment').length);
    });
    await page.waitForTimeout(600);
    const before = { slide: await opening.boundingBox(), signal: await signal.boundingBox() };

    await page.evaluate(() => window.__DECK_DEBUG__.goTo(1));
    await expect(page.locator('#deck-counter')).toHaveText('2 / 7');
    await page.waitForTimeout(800);
    await page.keyboard.press('ArrowLeft');
    await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
    await expect(opening).not.toHaveClass(/is-entering/);
    const after = { slide: await opening.boundingBox(), signal: await signal.boundingBox() };
    const stageBox = await stage.boundingBox();

    for (const part of ['slide', 'signal']) {
      for (const dimension of ['x', 'y', 'width', 'height']) {
        expect(Math.abs(after[part][dimension] - before[part][dimension])).toBeLessThanOrEqual(2);
      }
    }
    expect(after.signal.x).toBeGreaterThanOrEqual(stageBox.x);
    expect(after.signal.x + after.signal.width).toBeLessThanOrEqual(stageBox.x + stageBox.width);
  });
}

test('common presentation clicker keys navigate exactly one fragment step', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const dispatchKey = (key, code = '') => page.evaluate(({ value, physical }) => {
    document.dispatchEvent(new KeyboardEvent('keydown', { key: value, code: physical, bubbles: true, cancelable: true }));
  }, { value: key, physical: code });

  for (const key of ['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'Enter', 'MediaTrackNext', 'BrowserForward']) {
    await page.goto(deckUrl);
    await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
    await dispatchKey(key);
    await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
    await expect(page.locator('#slide-opening .fragment.is-revealed')).toHaveCount(1);
  }
  await page.goto(deckUrl);
  await dispatchKey('Enter', 'NumpadEnter');
  await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
  await expect(page.locator('#slide-opening .fragment.is-revealed')).toHaveCount(1);
  for (const key of ['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace', 'MediaTrackPrevious', 'BrowserBack']) {
    await page.goto(deckUrl);
    await page.evaluate(() => {
      const slide = document.querySelector('#slide-opening');
      window.__DECK_DEBUG__.setFragmentState(slide, slide.querySelectorAll('.fragment').length);
    });
    await dispatchKey(key);
    await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
    await expect(page.locator('#slide-opening .fragment.is-revealed')).toHaveCount(3);
  }
});

test('presentation controls consume fragment steps before changing slides', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto(deckUrl);
  const openingFragments = page.locator('#slide-opening .fragment');
  const fragmentCount = await openingFragments.count();
  expect(fragmentCount).toBeGreaterThan(1);
  await expect(page.locator('#slide-opening .fragment.is-revealed')).toHaveCount(0);

  await page.locator('#next-slide').click();
  await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
  await expect(page.locator('#slide-opening .fragment.is-revealed')).toHaveCount(1);
  for (let index = 2; index <= fragmentCount; index += 1) {
    await page.keyboard.press('PageDown');
    await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
    await expect(page.locator('#slide-opening .fragment.is-revealed')).toHaveCount(index);
  }
  await expect(page.locator('#next-slide')).toBeEnabled();

  await page.keyboard.press('PageDown');
  await expect(page.locator('#deck-counter')).toHaveText('2 / 7');

  await page.keyboard.press('PageUp');
  await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
  await expect(page.locator('#slide-opening .fragment.is-revealed')).toHaveCount(fragmentCount);

  await page.locator('#previous-slide').click();
  await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
  await expect(page.locator('#slide-opening .fragment.is-revealed')).toHaveCount(fragmentCount - 1);

  for (let index = fragmentCount - 2; index >= 0; index -= 1) {
    await page.keyboard.press('Backspace');
    await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
    await expect(page.locator('#slide-opening .fragment.is-revealed')).toHaveCount(index);
  }
  await expect(page.locator('#previous-slide')).toBeDisabled();
});

test('wheel and swipe use the same fragment-first navigation state', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto(deckUrl);
  await page.waitForTimeout(800);
  const stage = page.locator('#deck-stage');
  await stage.dispatchEvent('wheel', { deltaY: 120 });
  await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
  await expect(page.locator('#slide-opening .fragment.is-revealed')).toHaveCount(1);

  await stage.dispatchEvent('pointerdown', { clientX: 700, clientY: 450 });
  await stage.dispatchEvent('pointerup', { clientX: 580, clientY: 450 });
  await expect(page.locator('#deck-counter')).toHaveText('1 / 7');
  await expect(page.locator('#slide-opening .fragment.is-revealed')).toHaveCount(2);
});

test('presenter-controlled timeline steps reveal and move focus together', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto(deckUrl);
  await page.evaluate(() => {
    document.querySelector('#slide-timeline .timeline').removeAttribute('data-autoplay');
    window.__DECK_DEBUG__.goTo(3);
  });
  const timelineItems = page.locator('#slide-timeline .timeline-item');
  const revealedTimelineItems = page.locator('#slide-timeline .timeline-item.is-revealed');
  await expect(revealedTimelineItems).toHaveCount(0);

  await page.keyboard.press('PageDown');
  await expect(page.locator('#deck-counter')).toHaveText('4 / 7');
  await expect(timelineItems.nth(0)).toHaveClass(/is-active/);
  await expect(revealedTimelineItems).toHaveCount(1);

  await page.keyboard.press('PageDown');
  await expect(page.locator('#deck-counter')).toHaveText('4 / 7');
  await expect(timelineItems.nth(1)).toHaveClass(/is-active/);
  await expect(revealedTimelineItems).toHaveCount(2);

  await page.keyboard.press('PageUp');
  await expect(timelineItems.nth(0)).toHaveClass(/is-active/);
  await expect(revealedTimelineItems).toHaveCount(1);
});

test('remote iframe keeps a conservative network fallback visible', async ({ page }) => {
  await page.route('https://example.invalid/**', route => route.abort());
  await page.goto(remoteDeckUrl);
  await expect(page.locator('.embed-fallback')).toBeVisible();
  await expect(page.locator('.embed-status')).toContainText(/network|required/i);
  await page.waitForTimeout(250);
  await expect(page.locator('.embed-fallback')).toBeVisible();
  await expect(page.locator('.embed-status')).not.toContainText('Live');
});
