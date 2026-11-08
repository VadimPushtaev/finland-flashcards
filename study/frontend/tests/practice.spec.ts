import { test, expect } from './account.fixture';

test('practice chapter, automatic feedback and persisted FSRS review', async ({ page, context, account }) => {
  await context.addCookies([{ name: 'homebrew_session', value: account.token,
    url: 'http://127.0.0.1:18745' }]);
  await page.goto('/#/practice');
  await expect(page.locator('.practice-chapter')).toHaveCount(12);
  await expect(page.locator('.practice-chapter').first()).toContainText('44 kort att öva');
  await page.locator('.practice-chapter').first().click();
  await page.getByRole('button', { name: 'Starta övningen' }).click();
  await expect(page.locator('.practice-option')).toHaveCount(4);
  const first = await page.locator('.practice-question h2').textContent();
  expect(first?.length).toBeGreaterThan(10);
  await page.locator('.practice-answer').first().click();
  await expect(page.locator('.practice-feedback')).toBeVisible();
  await expect(page.locator('.practice-grades button[aria-pressed="true"]')).toHaveCount(1);
  await page.getByRole('button', { name: 'Hard' }).click();
  await expect(page.getByRole('button', { name: 'Hard' })).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('button', { name: 'Nästa →' }).click();
  await expect(page.locator('.practice-status')).toContainText('1 sparade svar');
  const overview = await context.request.get('/api/practice/overview');
  expect(overview.status()).toBe(200);
  expect((await overview.json()).chapters[0].new).toBe(43);
  await page.reload();
  await expect(page.getByRole('button', { name: 'Starta övningen' })).toBeVisible();
  expect(await page.evaluate(() => Object.keys(localStorage).filter(x => x.includes('practice')))).toEqual([]);
});

test('guest practice asks for login without changing account data', async ({ page }) => {
  await page.goto('/#/practice');
  await expect(page.getByRole('button', { name: 'Logga in', exact: true }).last()).toBeVisible();
  await expect(page.locator('.practice-question')).toHaveCount(0);
});

for (const theme of ['light', 'dark']) {
  test(`chapter priorities distinguish due, new, finished and empty decks in ${theme} mode`, async ({ page, context, account }, testInfo) => {
    await context.addCookies([{ name: 'homebrew_session', value: account.token,
      url: 'http://127.0.0.1:18745' }]);
    const preferences = await context.request.patch('/api/state/preferences', {
      headers: { 'X-Study-Request': '1', 'X-Study-User': account.username },
      data: { dark: theme === 'dark' },
    });
    expect(preferences.ok()).toBeTruthy();
    await page.route('**/api/practice/overview', async route => {
      const response = await route.fetch();
      const overview = await response.json();
      // Use real chapter metadata with representative personal study progress.
      Object.assign(overview.chapters[0], { new: 2, due: 3 });
      Object.assign(overview.chapters[1], { new: 8, due: 0 });
      Object.assign(overview.chapters[2], { new: 0, due: 0 });
      Object.assign(overview.chapters[3], { new: 0, due: 0, total: 0 });
      await route.fulfill({ response, json: overview });
    });
    await page.goto('/#/practice');
    await expect(page.locator('html')).toHaveAttribute('data-bs-theme', theme);
    const chapters = page.locator('.practice-chapter');
    await expect(chapters).toHaveCount(12);
    await expect(chapters.nth(0)).toContainText('Repetera först');
    await expect(chapters.nth(0)).toContainText('5 kort att öva');
    await expect(chapters.nth(0)).toContainText('2 nya');
    await expect(chapters.nth(0)).toContainText('3 att repetera');
    await expect(chapters.nth(1)).toContainText('Nya kort');
    await expect(chapters.nth(1)).toContainText('8 kort att öva');
    await expect(chapters.nth(2)).toContainText('Klart för nu');
    await expect(chapters.nth(2)).toContainText('0 kort att öva');
    await expect(chapters.nth(3)).toContainText('Inga kort');

    const accents = await chapters.evaluateAll(links => links.slice(0, 4)
      .map(link => getComputedStyle(link).borderInlineStartColor));
    expect(new Set(accents).size).toBe(4);
    await expect(chapters.nth(0).getByText('3 att repetera')).toHaveCSS('color', accents[0]);
    await expect(chapters.nth(0).getByText('2 nya')).toHaveCSS('color', accents[1]);
    await expect(chapters.nth(1).getByText('0 att repetera')).toHaveCSS('color', accents[3]);
    await expect(chapters.nth(2).getByText('0 nya')).toHaveCSS('color', accents[3]);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.screenshot({ path: testInfo.outputPath(`practice-${theme}.png`), fullPage: true });

    // The priority treatment preserves keyboard navigation to the chapter.
    await chapters.nth(0).focus();
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL(/#\/practice\/hb-c01$/);
    await expect(page.getByRole('button', { name: 'Starta övningen' })).toBeVisible();
  });
}
