import { test, expect } from './account.fixture';

test('practice shows only the reduced CORE set without optional-card controls', async ({ page, context, account }) => {
  await context.addCookies([{ name: 'homebrew_session', value: account.token,
    url: 'http://127.0.0.1:18745' }]);
  await page.goto('/#/practice');
  await expect(page.locator('.page-intro')).toContainText('CORE');
  const chapters = page.locator('.practice-chapter');
  await expect(chapters).toHaveCount(12);
  await expect(chapters.nth(4)).toContainText('59 kort att öva');
  await expect(chapters.nth(11)).toContainText('72 kort att öva');
  await expect(page.getByText(/EXTENDED|valfria kort/)).toHaveCount(0);
  await chapters.nth(11).click();
  const response = page.waitForResponse('/api/practice/chapters/hb-c12/queue');
  await page.getByRole('button', { name: 'Starta övningen' }).click();
  const data = await (await response).json();
  expect(data.cards).toHaveLength(72);
  expect(data.cards.every((card: { study_priority: string }) => card.study_priority === 'CORE')).toBe(true);
  await expect(page.getByRole('progressbar', { name: 'Kort i kapitlet' })).toHaveAttribute('aria-valuemax', '72');
});

test('practice keyboard shortcuts choose answers, grades and save with Enter', async ({ page, context, account }) => {
  await context.addCookies([{ name: 'homebrew_session', value: account.token,
    url: 'http://127.0.0.1:18745' }]);
  await page.goto('/#/practice/hb-c01');
  await page.getByRole('button', { name: 'Starta övningen' }).click();
  const grades = ['Again', 'Hard', 'Good', 'Easy'];
  for (let i = 0; i < 4; i++) {
    await expect(page.locator('.practice-answer').first()).toBeEnabled();
    const checked = page.waitForRequest(request => request.url().endsWith('/check'));
    await page.keyboard.press(String(i + 1));
    expect((await checked).postDataJSON()).toEqual({ option: i });
    await expect(page.locator('.practice-feedback')).toBeVisible();
    // Every number now changes the grade, without submitting another answer.
    for (let grade = 0; grade < 4; grade++) {
      await page.keyboard.press(String(grade + 1));
      await expect(page.getByRole('button', { name: grades[grade], exact: true }))
        .toHaveAttribute('aria-pressed', 'true');
    }
    await page.keyboard.press(String(i + 1));
    // Enter must advance even when a different grade button has keyboard focus.
    await page.getByRole('button', { name: 'Hard', exact: true }).focus();
    const reviewed = page.waitForRequest(request => request.url().endsWith('/review'));
    await page.keyboard.press('Enter');
    expect((await reviewed).postDataJSON()).toMatchObject({ option: i, grade: i + 1 });
    await expect(page.locator('.practice-feedback')).toHaveCount(0);
  }
});

test('practice shortcuts ignore editing, modifiers, held keys and pending answers', async ({ page, context, account }) => {
  await context.addCookies([{ name: 'homebrew_session', value: account.token,
    url: 'http://127.0.0.1:18745' }]);
  let releaseCheck!: () => void;
  const checkGate = new Promise<void>(resolve => { releaseCheck = resolve; });
  let checks = 0;
  let reviews = 0;
  await page.route('**/check', async route => {
    checks++;
    await checkGate;
    await route.fulfill({ json: { correct: true, correct_option: 0 } });
  });
  page.on('request', request => { if (request.url().endsWith('/review')) reviews++; });
  await page.goto('/#/practice/hb-c01');
  await page.getByRole('button', { name: 'Starta övningen' }).click();
  await expect(page.locator('.practice-answer').first()).toBeEnabled();
  await page.evaluate(() => {
    const input = document.createElement('input');
    document.body.append(input);
    input.focus();
    input.dispatchEvent(new KeyboardEvent('keydown', { key: '1', bubbles: true }));
    input.remove();
    const editor = document.createElement('div');
    editor.contentEditable = 'true';
    document.body.append(editor);
    editor.focus();
    editor.dispatchEvent(new KeyboardEvent('keydown', { key: '2', bubbles: true }));
    editor.remove();
    for (const modifiers of [{ ctrlKey: true }, { metaKey: true }, { altKey: true },
      { shiftKey: true }, { repeat: true }, { isComposing: true }]) {
      document.dispatchEvent(new KeyboardEvent('keydown', { key: '1', bubbles: true, ...modifiers }));
    }
  });
  await expect(page.locator('.practice-answer').first()).toBeEnabled();
  expect(checks).toBe(0);
  await page.keyboard.press('1');
  await expect.poll(() => checks).toBe(1);
  await page.keyboard.press('2');
  await page.keyboard.press('Enter');
  expect(checks).toBe(1);
  expect(reviews).toBe(0);
  releaseCheck();
  await expect(page.getByRole('button', { name: 'Good', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await page.evaluate(() => {
    document.dispatchEvent(new KeyboardEvent('keydown', { key: '1', repeat: true, bubbles: true }));
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', repeat: true, bubbles: true }));
  });
  await expect(page.getByRole('button', { name: 'Good', exact: true })).toHaveAttribute('aria-pressed', 'true');
  expect(reviews).toBe(0);
});

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
  await expect(page.getByRole('progressbar', { name: 'Kort i kapitlet' })).toHaveAttribute('aria-valuetext',
    '1 klara, 43 kvar i omgången, 0 utanför omgången');
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

test('card translations sit beside desktop cards or overlay the mobile bottom', async ({ page, context, account }, testInfo) => {
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
  const word = page.locator('.practice-option').first().getByRole('button', { name: 'solen', exact: true });
  await word.click();
  const panel = page.locator('.translation-panel');
  await expect(panel).toContainText('солнце');
  await expect(page.locator('.practice-feedback')).toHaveCount(0);
  await expect(page.getByText('Välj det här svaret')).toHaveCount(0);
  const viewport = page.viewportSize()!;
  const box = (await panel.boundingBox())!;
  if (viewport.width > 1000) {
    const card = (await page.locator('.practice-question').boundingBox())!;
    expect(box.x).toBeGreaterThanOrEqual(card.x + card.width);
    expect(box.y).toBeLessThan(card.y + 50);
  } else {
    const sheet = (await page.locator('.practice-translation-view').boundingBox())!;
    expect(sheet.height).toBeCloseTo((viewport.height - 44) / 2, 0);
    expect(sheet.y).toBeGreaterThan(viewport.height / 2 - 1);
    expect(box.y + box.height).toBeLessThanOrEqual(viewport.height);
    expect(await page.evaluate(() => document.documentElement.scrollHeight <= innerHeight)).toBe(true);
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: testInfo.outputPath('card-translation.png') });
  await page.getByRole('button', { name: 'Stäng översättningen' }).click();
  await expect(word).toBeFocused();
  const choose = page.getByRole('button', { name: 'Välj svar A', exact: true });
  expect((await choose.boundingBox())!.width).toBeGreaterThanOrEqual(44);
  await choose.click();
  await expect(page.locator('.practice-feedback')).toContainText('Rätt svar!');
  await expect(choose.locator('.bi-check-lg')).toHaveCount(1);
  if (viewport.width <= 1000) {
    const next = (await page.getByRole('button', { name: 'Nästa →' }).boundingBox())!;
    expect(next.y + next.height).toBeLessThanOrEqual(viewport.height);
    await expect(page.locator('.practice-option:visible')).toHaveCount(1);
    await page.getByRole('button', { name: 'Visa alla svar', exact: true }).click();
    await expect(page.locator('.practice-option:visible')).toHaveCount(4);
    await expect(page.locator('.practice-card-viewport')).toHaveCSS('overflow-y', 'auto');
    const expandedNext = (await page.getByRole('button', { name: 'Nästa →' }).boundingBox())!;
    expect(expandedNext.y + expandedNext.height).toBeLessThanOrEqual(viewport.height);
    await page.getByRole('button', { name: 'Visa färre svar', exact: true }).click();
    await expect(page.locator('.practice-option:visible')).toHaveCount(1);
  }
  await word.click();
  await expect(panel).toBeVisible();
  if (viewport.width <= 1000) {
    const sheet = (await page.locator('.practice-translation-view').boundingBox())!;
    const grading = (await page.locator('.practice-grading').boundingBox())!;
    expect(sheet.y + sheet.height).toBeLessThanOrEqual(grading.y + 1);
    await page.getByRole('button', { name: 'Nästa →' }).click();
    await expect(page.locator('.practice-finished')).toBeVisible();
  }
});

test('progress partitions chapter cards and keeps tiny-zone labels separate', async ({ page, context, account }) => {
  await context.addCookies([{ name: 'homebrew_session', value: account.token,
    url: 'http://127.0.0.1:18745' }]);
  await page.route('**/api/practice/chapters/hb-c01/queue', async route => {
    const response = await route.fetch();
    const data = await response.json();
    data.cards = data.cards.slice(0, 1);
    await route.fulfill({ response, json: data });
  });
  await page.goto('/#/practice/hb-c01');
  await page.getByRole('button', { name: 'Starta övningen' }).click();
  const progress = page.getByRole('progressbar', { name: 'Kort i kapitlet' });
  await expect(progress).toHaveAttribute('aria-valuetext', '0 klara, 1 kvar i omgången, 43 utanför omgången');
  for (const grade of ['Again', 'Hard']) {
    await page.locator('.practice-answer').first().click();
    await expect(page.locator('.practice-feedback')).toBeVisible();
    await page.getByRole('button', { name: grade, exact: true }).click();
    await page.getByRole('button', { name: 'Nästa →' }).click();
    await expect(progress).toHaveAttribute('aria-valuetext', grade === 'Again'
      ? '0 klara, 1 kvar i omgången, 43 utanför omgången'
      : '1 klara, 0 kvar i omgången, 43 utanför omgången');
  }
  await expect(page.locator('.practice-finished')).toBeVisible();
  const labels = await page.locator('.practice-progress-labels > div').evaluateAll(elements =>
    elements.map(element => {
      const box = element.getBoundingClientRect();
      return { left: box.left, right: box.right, width: element.clientWidth, scroll: element.scrollWidth };
    }));
  expect(labels[0].right).toBeLessThan(labels[1].left);
  expect(labels[1].right).toBeLessThan(labels[2].left);
  for (const label of labels) expect(label.scroll).toBeLessThanOrEqual(label.width);
});
