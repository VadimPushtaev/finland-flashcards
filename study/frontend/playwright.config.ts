import { defineConfig } from '@playwright/test';
import { randomUUID } from 'node:crypto';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

process.env.STUDY_E2E_DATABASE ||= join(tmpdir(), `homebrew-e2e-${randomUUID()}`, 'study.sqlite3');
process.env.STUDY_DATABASE_PATH = process.env.STUDY_E2E_DATABASE;

export default defineConfig({
  testDir: './tests',
  webServer: process.env.STUDY_URL ? undefined : {
    command: 'poetry run python ../tests/browser_server.py',
    url: 'http://127.0.0.1:18745/api/health',
    reuseExistingServer: false,
  },
  use: { baseURL: process.env.STUDY_URL || 'http://127.0.0.1:18745', trace: 'retain-on-failure' },
  projects: [
    { name: 'desktop', use: { viewport: { width: 1440, height: 1000 } } },
    { name: 'mobile-small', use: { viewport: { width: 320, height: 568 }, isMobile: true, hasTouch: true } },
    { name: 'mobile-375', use: { viewport: { width: 375, height: 812 }, isMobile: true, hasTouch: true } },
    { name: 'mobile', use: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
    { name: 'mobile-large', use: { viewport: { width: 430, height: 932 }, isMobile: true, hasTouch: true } },
    { name: 'mobile-landscape', use: { viewport: { width: 844, height: 390 }, isMobile: true, hasTouch: true } },
    { name: 'tablet', use: { viewport: { width: 768, height: 1024 }, isMobile: true, hasTouch: true } },
  ],
});
