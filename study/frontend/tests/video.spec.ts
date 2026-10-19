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
