import { test as base, expect } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';

type Account = { username: string; password: string; token: string };
const study = fileURLToPath(new URL('../../', import.meta.url));
function python(code: string, input: object) {
  return execFileSync('poetry', ['run', 'python', '-c', code], { cwd: study, input: JSON.stringify(input), encoding: 'utf8', env: process.env });
}
async function withAccount(use: (account: Account) => Promise<void>) {
    if (process.env.STUDY_URL) throw new Error('Account browser checks run only against the isolated local test server. Unset STUDY_URL.');
    const account = { username: `test-${randomUUID()}`, password: 'browser-test-password', token: randomUUID() + randomUUID() };
    python(`import json,sys,hashlib,time
from app.accounts import create_user
from app.database import database
x=json.load(sys.stdin)
create_user(x['username'],x['password'])
with database() as db:
 uid=db.execute('SELECT id FROM users WHERE username=?',(x['username'],)).fetchone()[0]
 db.execute('INSERT INTO sessions VALUES (?,?,?)',(hashlib.sha256(x['token'].encode()).hexdigest(),uid,int(time.time())))`, account);
    try { await use(account); }
    finally { python(`import json,sys
from app.database import database
x=json.load(sys.stdin)
with database() as db: db.execute('DELETE FROM users WHERE username=?',(x['username'],))`, account); }
}
export const test = base.extend<{ account: Account; otherAccount: Account }>({
  account: async ({}, use) => withAccount(use),
  otherAccount: async ({}, use) => withAccount(use),
});
export { expect };
