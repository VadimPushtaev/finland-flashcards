import { test, expect } from './account.fixture';

test.skip(({ isMobile }) => isMobile, 'Desktop layout; mobile has its own unchanged practice view.');

for (const viewport of [
  { width: 1440, height: 900 },
  // Smaller CSS viewports also exercise the space available at browser zoom.
  { width: 1280, height: 720 },
  { width: 1100, height: 600 },
  { width: 1001, height: 500 },
]) {
  for (const theme of ['light', 'dark']) {
    test(`readable answers and visible feedback at ${viewport.width}×${viewport.height}, ${theme}`, async ({ page, context, account }, testInfo) => {
      await page.setViewportSize(viewport);
      await context.addCookies([{ name: 'homebrew_session', value: account.token,
        url: 'http://127.0.0.1:18745' }]);
      await context.request.patch('/api/state/preferences', {
        headers: { 'X-Study-Request': '1', 'X-Study-User': account.username },
        data: { dark: theme === 'dark' },
      });
      await page.route('**/api/practice/chapters/hb-c03/queue', async route => {
        const response = await route.fetch();
        const data = await response.json();
        data.cards = data.cards.filter((card: { id: string }) => card.id === 'hb-c03-midsommar-0002');
        await route.fulfill({ response, json: data });
      });
      await page.goto('/#/practice/hb-c03');
      await page.getByRole('button', { name: 'Starta övningen' }).click();
      await expect(page.locator('.practice-question h2')).toContainText('Vilken eldtradition');
      expect(await page.locator('.practice-option-text').first()
        .evaluate(el => parseFloat(getComputedStyle(el).fontSize))).toBeGreaterThanOrEqual(20);
      for (const answer of await page.locator('.practice-answer').all()) {
        // Very short windows may scroll the question, but never the result footer.
        if (viewport.height < 600) await answer.scrollIntoViewIfNeeded();
        // Allow subpixel rounding at the scroll boundary.
        await expect(answer).toBeInViewport({ ratio: .99 });
        expect((await answer.boundingBox())!.width).toBeGreaterThanOrEqual(44);
      }
      await page.getByRole('button', { name: 'Välj svar A', exact: true }).click();
      await expect(page.locator('.practice-feedback')).toContainText('Rätt svar: B');
      await expect(page.locator('.practice-feedback')).toBeInViewport({ ratio: 1 });
      await expect(page.locator('.practice-option.is-correct')).toContainText('midsommarbrasor');
      await expect(page.locator('.practice-option.is-correct')).toBeInViewport({ ratio: 1 });
      await expect(page.getByRole('button', { name: 'Nästa →' })).toBeInViewport({ ratio: 1 });
      expect(await page.evaluate(() => document.documentElement.scrollHeight <= innerHeight)).toBe(true);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      await page.screenshot({ path: testInfo.outputPath('desktop-result.png') });
      await page.getByRole('button', { name: 'Good', exact: true }).click();
      await page.getByRole('button', { name: 'Nästa →' }).click();
      await expect(page.locator('.practice-finished')).toBeVisible();
    });
  }
}

test('long desktop cards scroll without losing feedback, grading or Next', async ({ page, context, account }, testInfo) => {
  await page.setViewportSize({ width: 1100, height: 600 });
  await context.addCookies([{ name: 'homebrew_session', value: account.token,
    url: 'http://127.0.0.1:18745' }]);
  await page.route('**/api/practice/chapters/hb-c03/queue', async route => {
    const response = await route.fetch();
    const data = await response.json();
    const card = data.cards.find((card: { id: string }) => card.id === 'hb-c03-midsommar-0002');
    data.cards = [{ ...card, question: card.question.repeat(8),
      options: card.options.map((option: string) => Array(5).fill(option).join('. ')) }];
    await route.fulfill({ response, json: data });
  });
  // The stress fixture intentionally differs from the reviewed translation surfaces.
  await page.route('**/cards/*/translation', route => route.fulfill({
    json: { available: false, language: 'ru', records: {} },
  }));
  await page.goto('/#/practice/hb-c03');
  await page.getByRole('button', { name: 'Starta övningen' }).click();
  const viewport = page.locator('.practice-card-viewport');
  await page.getByRole('button', { name: 'Välj svar D', exact: true }).click();
  await expect(page.locator('.practice-feedback')).toBeInViewport({ ratio: 1 });
  await expect(page.getByRole('button', { name: 'Nästa →' })).toBeInViewport({ ratio: 1 });
  await expect(page.locator('.practice-option.is-correct .practice-answer')).toBeInViewport({ ratio: 1 });
  await page.getByRole('button', { name: 'Visa alla svar', exact: true }).click();
  await expect(page.locator('.practice-option:visible')).toHaveCount(4);
  await viewport.evaluate(el => { el.scrollTop = el.scrollHeight; });
  await expect(page.getByRole('button', { name: 'Välj svar D', exact: true })).toBeInViewport({ ratio: 1 });
  await expect(page.locator('.practice-feedback')).toBeInViewport({ ratio: 1 });
  await expect(page.getByRole('button', { name: 'Nästa →' })).toBeInViewport({ ratio: 1 });
  const cardArea = (await viewport.boundingBox())!;
  const footer = (await page.locator('.practice-grading').boundingBox())!;
  expect(cardArea.y + cardArea.height).toBeLessThanOrEqual(footer.y);
  await page.getByRole('button', { name: 'Visa statistik', exact: true }).click();
  await expect(page.locator('.practice-stats')).toBeInViewport({ ratio: 1 });
  await expect(page.getByRole('button', { name: 'Nästa →' })).toBeInViewport({ ratio: 1 });
  await page.getByRole('button', { name: 'Dölj statistik', exact: true }).click();
  await page.screenshot({ path: testInfo.outputPath('long-desktop-card.png') });
  await page.getByRole('button', { name: 'Good', exact: true }).click();
  await page.getByRole('button', { name: 'Nästa →' }).click();
  await expect(page.locator('.practice-finished')).toBeVisible();
});

test('translation, viewport changes and save errors keep Next reachable', async ({ page, context, account }, testInfo) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await context.addCookies([{ name: 'homebrew_session', value: account.token,
    url: 'http://127.0.0.1:18745' }]);
  await page.route('**/api/practice/chapters/hb-c01/queue', async route => {
    const response = await route.fetch();
    const data = await response.json();
    data.cards = data.cards.filter((card: { id: string }) => card.id === 'hb-c01-arstider-0002');
    await route.fulfill({ response, json: data });
  });
  await page.goto('/#/practice/hb-c01');
  await page.getByRole('button', { name: 'Starta övningen' }).click();
  await page.getByRole('button', { name: 'Välj svar A', exact: true }).click();
  await expect(page.locator('.practice-feedback')).toContainText('Rätt svar!');
  await page.locator('.practice-option').first().getByRole('button', { name: 'solen', exact: true }).click();
  await expect(page.locator('.translation-panel')).toContainText('солнце');
  for (const viewport of [{ width: 1001, height: 500 }, { width: 768, height: 1024 }, { width: 1100, height: 600 }]) {
    await page.setViewportSize(viewport);
    await expect(page.locator('.practice-feedback')).toHaveCount(1);
    await expect(page.locator('.translation-panel')).toBeInViewport({ ratio: 1 });
    await expect(page.getByRole('button', { name: 'Nästa →' })).toBeInViewport({ ratio: 1 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
  await page.screenshot({ path: testInfo.outputPath('desktop-translation-result.png') });
  await page.getByRole('button', { name: 'Stäng översättningen' }).click();
  await page.route('**/api/practice/chapters/hb-c01/review', route => route.fulfill({
    status: 500, json: { detail: 'Kunde inte spara svaret. Försök igen.' },
  }), { times: 1 });
  await page.getByRole('button', { name: 'Nästa →' }).click();
  await expect(page.locator('.practice-page > .alert')).toContainText('Kunde inte spara svaret');
  await expect(page.getByRole('button', { name: 'Nästa →' })).toBeInViewport({ ratio: 1 });
  await page.getByRole('button', { name: 'Nästa →' }).click();
  await expect(page.locator('.practice-finished')).toBeVisible();
});
