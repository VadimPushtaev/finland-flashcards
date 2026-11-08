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
