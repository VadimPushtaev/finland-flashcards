import { test, expect } from '@playwright/test';

test('read, save, complete and resume a section across reloads', async ({ page }, testInfo) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Lär känna Finland. Ett kapitel i taget.' })).toBeVisible();
  await expect(page.locator('.chapter-card')).toHaveCount(12);
  await page.getByRole('link', { name: /Börja läsa/ }).click();
  await expect(page.getByRole('heading', { name: 'Finland i Norden', exact: true })).toBeVisible();
  await expect(page.locator('#hb-c01-u0001')).toContainText('Finland är ett land i norra Europa');
  const bookmark = page.locator('#hb-c01-u0001').getByRole('button', { name: 'Spara textstycke' });
  if (testInfo.project.use.hasTouch) {
    expect(await bookmark.evaluate(element => Number(getComputedStyle(element).opacity))).toBeGreaterThan(0);
    await bookmark.tap();
  } else {
    await page.locator('#hb-c01-u0001').hover();
    await bookmark.click();
  }
  await page.getByRole('button', { name: 'Markera som läst', exact: true }).click();
  await page.reload();
  await expect(page.getByRole('button', { name: 'Markera som oläst' })).toBeVisible();
  await expect(page.locator('#hb-c01-u0001').getByRole('button', { name: 'Ta bort bokmärke' })).toHaveAttribute('aria-pressed', 'true');
  await page.goto('/#/saved');
  await expect(page.locator('.passage-card')).toHaveCount(1);
  await page.getByRole('link', { name: /Läs i sitt sammanhang/ }).click();
  await expect(page.locator('#hb-c01-u0001')).toHaveClass(/target-unit/);
  await page.goto('/');
  await expect(page.getByRole('link', { name: /Fortsätt läsa/ })).toBeVisible();
});

test('search Swedish text and navigate to a matching original passage', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('searchbox', { name: 'Sök i materialet' }).fill('rösträtt');
  await page.getByRole('searchbox', { name: 'Sök i materialet' }).press('Enter');
  await expect(page.getByRole('heading', { name: 'Resultat för ”rösträtt”' })).toBeVisible();
  await expect(page.locator('.passage-card').first()).toBeVisible();
  await page.locator('.passage-card a').first().click();
  await expect(page.locator('.target-unit')).toContainText(/rösträtt/i);
});

test('reading preferences persist and layout fits the screen', async ({ page }) => {
  await page.goto('/#/chapter/hb-c01/hb-c01-lage');
  await expect(page.locator('.reader-text')).toBeVisible();
  await page.getByRole('button', { name: 'Öka textstorleken' }).click();
  await page.getByRole('button', { name: 'Aktivera mörkt tema' }).click();
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-bs-theme', 'dark');
  await expect(page.locator('.reader-text')).toHaveCSS('font-size', '22px');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test('mobile navigation and section selection work', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'desktop');
  await page.goto('/');
  const menu = page.getByRole('button', { name: 'Öppna menyn' });
  if (await menu.isVisible()) await menu.tap();
  await page.getByRole('navigation', { name: 'Kapitel', exact: true }).getByRole('link', { name: /Historia/ }).click();
  await expect(page.locator('.sidebar')).not.toHaveClass(/is-open/);
  await page.getByRole('combobox', { name: 'Välj avsnitt' }).selectOption('hb-c02-sverige');
  await expect(page.getByRole('heading', { name: 'Svenskt styre, reformation och upplysning' })).toBeVisible();
});

test('overview, search, bookmarks and expanded sources fit the viewport', async ({ page }) => {
  const assertFits = async () => {
    const size = await page.evaluate(() => ({ width: window.innerWidth, content: document.documentElement.scrollWidth }));
    expect(size.content, `content width ${size.content} exceeds viewport ${size.width}`).toBeLessThanOrEqual(size.width);
  };
  await page.goto('/');
  await expect(page.locator('.chapter-card')).toHaveCount(12);
  await assertFits();
  await page.goto('/#/search/medborgarskap');
  await expect(page.locator('.passage-card').first()).toBeVisible();
  await assertFits();
  await page.goto('/#/saved');
  await expect(page.getByRole('heading', { name: 'En plats för det viktiga' })).toBeVisible();
  await assertFits();
  await page.goto('/#/about');
  await expect(page.locator('.attribution-card')).toHaveCount(3);
  for (const details of await page.locator('.attribution-card summary').all()) await details.click();
  await assertFits();
  await page.goto('/#/chapter/hb-c12');
  await expect(page.locator('.reader-text')).toBeVisible();
  await page.getByRole('button', { name: 'Öka textstorleken' }).click();
  await page.getByRole('button', { name: 'Öka textstorleken' }).click();
  await page.locator('.source-details summary').click();
  await expect(page.locator('.source-details li').first()).not.toContainText('Källorna hämtas');
  await assertFits();
});

test('chapter menu remains reachable on short screens', async ({ page }) => {
  await page.goto('/');
  const menu = page.getByRole('button', { name: 'Öppna menyn' });
  if (await menu.isVisible()) await menu.click();
  const lastChapter = page.getByRole('navigation', { name: 'Kapitel', exact: true }).getByRole('link', { name: /Integration/ });
  await lastChapter.scrollIntoViewIfNeeded();
  await lastChapter.click();
  await expect(page.locator('.reader-chapter-title')).toHaveText('Integration, uppehåll och medborgarskap');
});
