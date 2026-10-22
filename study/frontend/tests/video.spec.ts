import { test, expect } from '@playwright/test';

test('available section video plays inline and disappears on navigation', async ({ page }) => {
  await page.goto('/#/chapter/hb-c01/hb-c01-lage');
  const video = page.getByLabel('Video: Finland i Norden');
  await expect(video).toBeVisible();
  await expect(video).toHaveAttribute('controls', '');
  await expect(video).toHaveAttribute('preload', 'none');
  await expect(page.getByRole('link', { name: 'Videons källor och upphov' })).toBeVisible();
  await video.evaluate(async (element: HTMLVideoElement) => {
    element.muted = true;
    await element.play();
  });
  await expect.poll(() => video.evaluate((element: HTMLVideoElement) => element.currentTime)).toBeGreaterThan(0);
  const bounds = await video.boundingBox();
  expect(bounds!.width).toBeLessThanOrEqual(page.viewportSize()!.width);
  await page.goto('/#/chapter/hb-c02');
  await expect(page.locator('.reader-chapter-title')).toBeVisible();
  await expect(page.locator('video')).toHaveCount(0);
});

test('switches audio while playing and paused, retaining position and seeking', async ({ page }) => {
  test.skip(process.env.STUDY_E2E_VIDEO_TRACKS !== '1', 'Requires synthetic bilingual media fixture');
  const mediaRequests: string[] = [];
  page.on('request', request => { if (request.url().endsWith('.m4s')) mediaRequests.push(request.url()); });
  await page.goto('/#/chapter/hb-c01/hb-c01-lage');
  const video = page.getByLabel('Video: Finland i Norden');
  const language = page.getByLabel('Ljudspråk');
  await expect(language).toHaveValue('sv');
  await expect(video).toBeVisible();
  await expect(video).toHaveAttribute('controls', '');
  await video.evaluate(async (element: HTMLVideoElement) => { element.muted = true; await element.play(); });
  await expect.poll(() => video.evaluate((element: HTMLVideoElement) => element.currentTime)).toBeGreaterThan(0);
  await video.evaluate((element: HTMLVideoElement) => { element.currentTime = 7; element.playbackRate = 1.5; });
  await language.selectOption('ru');
  await expect.poll(() => mediaRequests.some(url => url.endsWith('/ru.m4s'))).toBe(true);
  await expect.poll(() => video.evaluate((element: HTMLVideoElement) => element.currentTime)).toBeGreaterThanOrEqual(7);
  await expect.poll(() => video.evaluate((element: HTMLVideoElement) => element.paused)).toBe(false);
  expect(await video.evaluate((element: HTMLVideoElement) => element.playbackRate)).toBe(1.5);
  await video.evaluate((element: HTMLVideoElement) => { element.pause(); element.currentTime = 4; });
  await language.selectOption('sv');
  await expect.poll(() => video.evaluate((element: HTMLVideoElement) => element.currentTime)).toBeCloseTo(4, 0);
  expect(await video.evaluate((element: HTMLVideoElement) => element.paused)).toBe(true);
  await video.evaluate(async (element: HTMLVideoElement) => { element.currentTime = 12; await element.play(); });
  await expect.poll(() => video.evaluate((element: HTMLVideoElement) => element.currentTime)).toBeGreaterThan(12);
  expect(mediaRequests.some(url => url.endsWith('/sv.m4s'))).toBe(true);
  expect(new Set(mediaRequests.filter(url => url.endsWith('/video.m4s'))).size).toBe(1);
  await expect(page.getByRole('alert')).toHaveCount(0);
});
