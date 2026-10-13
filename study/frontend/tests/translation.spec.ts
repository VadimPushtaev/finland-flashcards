import { test, expect } from './account.fixture';

const first = '/#/chapter/hb-c01/hb-c01-lage';
const wordSelector = '#hb-c01-u0001 button.translation-word';

test('word and sentence translations share the screen without covering the reader', async ({ page }, info) => {
  await page.goto(first);
  const word = page.locator(wordSelector).filter({ hasText: /^skogar$/ });
  if (info.project.use.hasTouch) await word.tap(); else await word.click();
  const panel = page.getByRole('complementary', { name: 'Rysk översättning' });
  await expect(panel).toBeVisible();
  await expect(panel.locator('.word-meaning h2')).toHaveText('skog');
  await expect(panel.locator('.context-meaning')).toHaveText('леса');
  await expect(panel.locator('.sentence-meaning > p')).toContainText('леса и озёра');
  await expect(page.locator('[data-sentence-id="hb-c01-u0001-s001"]')).toHaveClass('selected-sentence');
  await panel.getByText('Ordbok', { exact: true }).click();
  await expect(panel.locator('.dictionary-meaning')).toContainText('Существительное');
  await panel.getByText('Svenskt original', { exact: true }).click();
  await expect(panel.locator('.sentence-meaning details p')).toContainText('skogar och sjöar');
  const a = await page.locator('.reading-column').boundingBox();
  const b = await panel.boundingBox();
  expect(a && b && (a.x + a.width <= b.x + 1 || a.y + a.height <= b.y + 1)).toBeTruthy();
  expect(a!.height).toBeGreaterThan(150);
  expect(b!.height).toBeGreaterThan(150);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  // Scrolling the text pane must not move the panel or its scroll position.
  const panelScroll = await panel.evaluate(el => el.scrollTop);
  await page.locator('.reading-column').evaluate(el => { el.scrollTop += 200; });
  expect(await panel.evaluate(el => el.scrollTop)).toBe(panelScroll);
  await panel.getByRole('button', { name: 'Stäng översättningen' }).click();
  await expect(panel).toHaveCount(0);
  await expect(word).toBeFocused();
});

test('function words retain sentence support and keyboard selection works', async ({ page }) => {
  await page.goto(first);
  const word = page.locator(wordSelector).filter({ hasText: /^är$/ }).first();
  await word.focus();
  await word.press('Enter');
  await expect(page.locator('.translation-panel')).toContainText('Ingen separat ordförklaring');
  await expect(page.locator('.sentence-meaning > p')).toContainText('Финляндия');
  await word.press('Escape');
  await expect(page.locator('.translation-panel')).toHaveCount(0);
  await expect(word).toBeFocused();
  await page.locator('#hb-c01-u0002 .translation-word').filter({ hasText: /^hör till$/ }).click();
  await expect(page.locator('.word-meaning h2')).toHaveText('höra till');
  await expect(page.locator('.context-meaning')).toHaveText('относится к');
});

test('section navigation clears selection and unavailable sections remain readable', async ({ page }) => {
  // Keep the unavailable-state check independent of translation progress.
  await page.route('**/sections/hb-c01-regioner/translation', route => route.fulfill({
    json: { available: false, language: 'ru', records: {} },
  }));
  await page.goto(first);
  await page.locator(wordSelector).first().click();
  await page.locator('.reader-contents summary').click();
  await page.getByRole('combobox', { name: 'Välj avsnitt' }).selectOption('hb-c01-regioner');
  await expect(page.locator('.translation-panel')).toHaveCount(0);
  await expect(page.locator('.translation-hint')).toContainText('finns inte');
  await expect(page.locator('.reader-text')).toContainText('De olika områdena');
  await expect(page.locator('.translation-word')).toHaveCount(0);
  await page.locator('.reader-contents summary').click();
  await page.getByRole('combobox', { name: 'Välj kapitel' }).selectOption('hb-c12');
  await expect(page.locator('.reader-chapter-title')).toHaveText('Integration, uppehåll och medborgarskap');
});

test('translation survives large text, dark theme, and orientation changes', async ({ page, context, account }) => {
  await context.addCookies([{ name: 'homebrew_session', value: account.token, url: 'http://127.0.0.1:18745' }]);
  await page.goto(first);
  await page.getByRole('button', { name: 'Öka textstorleken' }).click();
  await expect(page.locator('.reader-text')).toHaveCSS('font-size', '22px');
  await page.getByRole('button', { name: 'Öka textstorleken' }).click();
  await expect(page.locator('.reader-text')).toHaveCSS('font-size', '24px');
  await page.getByRole('button', { name: 'Aktivera mörkt tema' }).click();
  await page.locator(wordSelector).filter({ hasText: /^naturförhållandena$/ }).click();
  await expect(page.locator('.word-meaning h2')).toHaveText('naturförhållande');
  for (const viewport of [{ width: 320, height: 568 }, { width: 844, height: 390 }]) {
    await page.setViewportSize(viewport);
    await expect(page.locator('.translation-panel')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const a = await page.locator('.reading-column').boundingBox();
    const b = await page.locator('.translation-panel').boundingBox();
    expect(a!.height).toBeGreaterThan(150);
    expect(b!.height).toBeGreaterThan(150);
  }
});

test('failed translation request offers retry without hiding Swedish text', async ({ page }) => {
  let fail = true;
  await page.route('**/sections/*/translation', async route => {
    if (fail) await route.fulfill({ status: 503, body: '{}' }); else await route.continue();
  });
  await page.goto(first);
  await expect(page.locator('.reader-text')).toContainText('Finland är ett land');
  await expect(page.locator('.translation-hint')).toContainText('kunde inte hämtas');
  fail = false;
  await page.locator('.translation-hint').getByRole('button', { name: 'Försök igen' }).click();
  await page.locator(wordSelector).first().click();
  await expect(page.locator('.translation-panel')).toBeVisible();
});

test('discontinuous expressions select all spans and Unicode offsets preserve exact text', async ({ page }) => {
  const text = '😀 Hon tycker verkligen om samhällskunskap.';
  const sentence = 'hb-c01-u0001-s001';
  const span = (word: string) => { const start = Array.from(text.slice(0, text.indexOf(word))).length; return { start, end: start + Array.from(word).length, text: word }; };
  await page.route('**/api/chapters/hb-c01', async route => {
    const response = await route.fetch();
    const chapter = await response.json();
    chapter.sections[0].blocks = [{ type: 'paragraph', id: 'hb-c01-u0001', text, sentences: [{ id: sentence, start: 0, end: Array.from(text).length }] }];
    await route.fulfill({ json: chapter });
  });
  await page.route('**/sections/hb-c01-lage/translation', route => route.fulfill({ json: { available: true, language: 'ru', records: {
    [sentence]: { source_id: sentence, sv: text, ru: 'Ей действительно нравится обществознание.', vocabulary: [
      { lemma: 'tycka om', pos: 'VERB', context_ru: 'нравится', general_ru: 'любить', spans: [span('tycker'), span('om')] },
      { lemma: 'verkligen', pos: 'ADV', context_ru: 'действительно', general_ru: 'действительно', spans: [span('verkligen')] },
    ] },
  } } }));
  await page.goto(first);
  await expect(page.locator('#hb-c01-u0001 > span')).toHaveText(text);
  await page.locator(wordSelector).filter({ hasText: /^om$/ }).click();
  await expect(page.locator('.word-meaning h2')).toHaveText('tycka om');
  await expect(page.locator('.selected-word')).toHaveCount(2);
  await page.locator(wordSelector).filter({ hasText: /^verkligen$/ }).click();
  await expect(page.locator('.word-meaning h2')).toHaveText('verkligen');
  await expect(page.locator('.selected-word')).toHaveCount(1);
});
