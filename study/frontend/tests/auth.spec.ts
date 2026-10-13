import { test, expect } from './account.fixture';

const first = '/#/chapter/hb-c01/hb-c01-lage';

test('guest saving prompts, cancel leaves state unchanged, and login replays once', async ({ page, account }) => {
  await page.goto(first);
  await expect(page.locator('.reader-text')).toBeVisible();
  await expect(page.getByRole('dialog')).toHaveCount(0);
  const bookmark = page.locator('#hb-c01-u0001 .unit-bookmark');
  await bookmark.click();
  const dialog = page.getByRole('dialog', { name: 'Logga in' });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByLabel('Användarnamn')).toBeFocused();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await dialog.getByRole('button', { name: 'Avbryt' }).click();
  await expect(bookmark).toHaveAttribute('aria-pressed', 'false');
  await expect(bookmark).toBeFocused();
  await bookmark.click();
  await dialog.getByLabel('Användarnamn').fill(account.username);
  await dialog.getByLabel('Lösenord').fill('wrong-password');
  await dialog.getByRole('button', { name: 'Logga in', exact: true }).click();
  await expect(dialog.getByRole('alert')).toContainText('Fel användarnamn');
  await dialog.getByLabel('Lösenord').fill(account.password);
  await dialog.getByRole('button', { name: 'Logga in', exact: true }).click();
  await expect(dialog).toHaveCount(0);
  await expect(bookmark).toHaveAttribute('aria-pressed', 'true');
  await page.reload();
  await expect(bookmark).toHaveAttribute('aria-pressed', 'true');
  const state = await page.request.get('/api/state');
  expect((await state.json()).bookmarks).toEqual(['hb-c01-u0001']);
  expect(await page.evaluate(() => localStorage.getItem('homebrew-study-v1'))).toBeNull();
  await page.getByRole('button', { name: 'Logga ut' }).click();
  await expect(bookmark).toHaveAttribute('aria-pressed', 'false');
  await page.getByRole('button', { name: 'Öka textstorleken' }).click();
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: 'Avbryt' }).click();
  await expect(page.locator('.reader-text')).toHaveCSS('font-size', '20px');
});

test('same account works in another browser and failed saves are not displayed', async ({ page, context, browser, account }) => {
  await context.addCookies([{ name: 'homebrew_session', value: account.token, url: 'http://127.0.0.1:18745' }]);
  await page.goto(first);
  const bookmark = page.locator('#hb-c01-u0001 .unit-bookmark');
  await bookmark.click();
  await expect(bookmark).toHaveAttribute('aria-pressed', 'true');
  const second = await browser.newContext();
  await second.addCookies([{ name: 'homebrew_session', value: account.token, url: 'http://127.0.0.1:18745' }]);
  const other = await second.newPage();
  await other.goto('http://127.0.0.1:18745/#/saved');
  await expect(other.locator('.passage-card')).toHaveCount(1);
  await page.route('**/api/state/completed/*', route => route.fulfill({ status: 503, json: { detail: 'Kunde inte spara. Försök igen.' } }));
  await page.getByRole('button', { name: 'Markera som läst', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('Kunde inte spara');
  await expect(page.getByRole('button', { name: 'Markera som läst', exact: true })).toHaveAttribute('aria-pressed', 'false');
  await page.unroute('**/api/state/completed/*');
  // Simulate revocation without logging out this page's in-memory account state.
  await context.request.post('/api/auth/logout', { headers: { 'X-Study-Request': '1' } });
  await page.getByRole('button', { name: 'Markera som läst', exact: true }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(bookmark).toHaveAttribute('aria-pressed', 'false');
  await second.close();
});


test('a stale account tab cannot save into a newly selected account', async ({ page, context, account, otherAccount }) => {
  await context.addCookies([{ name: 'homebrew_session', value: account.token, url: 'http://127.0.0.1:18745' }]);
  const position = page.waitForResponse(response => response.url().endsWith('/api/state/position'));
  await page.goto(first);
  await expect(page.locator('.reader-text')).toBeVisible();
  await (await position).finished();
  // Another tab logs into a different account: browser cookies are shared.
  await context.addCookies([{ name: 'homebrew_session', value: otherAccount.token, url: 'http://127.0.0.1:18745' }]);
  await page.locator('#hb-c01-u0001 .unit-bookmark').click();
  await expect(page.getByRole('dialog')).toBeVisible();
  const state = await context.request.get('/api/state');
  expect((await state.json()).bookmarks).toEqual([]);
  await page.getByRole('dialog').getByRole('button', { name: 'Avbryt' }).click();
  await page.reload();
  await expect(page.locator('.account-name')).toHaveText(otherAccount.username);
  await expect(page.locator('#hb-c01-u0001 .unit-bookmark')).toHaveAttribute('aria-pressed', 'false');
});
