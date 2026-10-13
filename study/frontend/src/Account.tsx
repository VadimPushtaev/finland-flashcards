import { useCallback, useEffect, useRef, useState } from 'react';

export type Progress = { completed: string[]; bookmarks: string[]; last: { chapter: string; section: string } | null; size: number; serif: boolean; dark: boolean };
export const defaultProgress: Progress = { completed: [], bookmarks: [], last: null, size: 20, serif: true, dark: false };
type Action = { path: string; method: string; body: object; patch: (p: Progress) => Progress };
class RequestError extends Error { status: number; constructor(status: number, message: string) { super(message); this.status = status; } }
async function request<T>(path: string, method = 'GET', body?: object, expectedUser?: string): Promise<T> {
  const headers: Record<string, string> = method === 'GET' ? {} : { 'Content-Type': 'application/json', 'X-Study-Request': '1' };
  if (expectedUser) headers['X-Study-User'] = expectedUser;
  const response = await fetch(path, { method, credentials: 'same-origin', headers, body: body ? JSON.stringify(body) : undefined });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new RequestError(response.status, typeof data.detail === 'string' ? data.detail : 'Kunde inte spara. Försök igen.');
  }
  return response.json();
}

export function useAccount() {
  const [progress, setProgress] = useState<Progress>(defaultProgress);
  const [username, setUsername] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const [saveError, setSaveError] = useState('');
  const pending = useRef<Action | null>(null);
  const userRef = useRef<string | null>(null);
  const generation = useRef(0);
  const revision = useRef(0);
  const queue = useRef<Promise<void>>(Promise.resolve());
  const stateRef = useRef(progress);
  stateRef.current = progress;
  const assignUser = (name: string | null) => { userRef.current = name; setUsername(name); };
  const execute = useCallback((action: Action, background = false) => {
    if (!userRef.current) {
      if (!background) { pending.current = action; setLoginOpen(true); }
      return;
    }
    const version = generation.current;
    const expectedUser = userRef.current;
    revision.current++;
    queue.current = queue.current.then(async () => {
      if (version !== generation.current || !userRef.current) return;
      try {
        await request(action.path, action.method, action.body, expectedUser);
        if (version === generation.current) { setProgress(p => action.patch(p)); setSaveError(''); }
      } catch (e) {
        if (version !== generation.current) return;
        const error = e as RequestError;
        if (error.status === 401) {
          generation.current++;
          assignUser(null); setProgress(defaultProgress);
          if (!background) { pending.current = action; setLoginOpen(true); }
          setSaveError('Logga in igen för att spara.');
        } else setSaveError(error.message);
      }
    });
  }, []);
  useEffect(() => {
    // Old browser state is intentionally discarded; account data starts fresh.
    try { localStorage.removeItem('homebrew-study-v1'); } catch { /* Storage may be disabled. */ }
    let cancelled = false;
    const version = generation.current;
    const restore = async () => {
      try {
        const session = await request<{ user: { username: string } | null }>('/api/auth/session');
        const state = session.user ? await request<Progress>('/api/state', 'GET', undefined, session.user.username) : defaultProgress;
        if (!cancelled && version === generation.current) { setProgress(state); assignUser(session.user?.username || null); }
      } catch { if (!cancelled) setSaveError('Kontot kunde inte hämtas. Logga in för att spara.'); }
      finally { if (!cancelled) setReady(true); }
    };
    void restore();
    return () => { cancelled = true; };
  }, []);
  useEffect(() => { document.documentElement.setAttribute('data-bs-theme', progress.dark ? 'dark' : 'light'); }, [progress.dark]);
  useEffect(() => {
    const refresh = async () => {
      if (!userRef.current || document.hidden) return;
      const version = generation.current;
      await queue.current;
      const latest = revision.current;
      try {
        const session = await request<{ user: { username: string } | null }>('/api/auth/session');
        const name = session.user?.username || null;
        const state = name ? await request<Progress>('/api/state', 'GET', undefined, name) : defaultProgress;
        if (version === generation.current && latest === revision.current) {
          if (name !== userRef.current) { generation.current++; pending.current = null; assignUser(name); }
          setProgress(state);
        }
      } catch (e) {
        if (version === generation.current && (e as RequestError).status === 401) {
          generation.current++; assignUser(null); setProgress(defaultProgress);
        }
      }
    };
    window.addEventListener('focus', refresh);
    document.addEventListener('visibilitychange', refresh);
    return () => { window.removeEventListener('focus', refresh); document.removeEventListener('visibilitychange', refresh); };
  }, []);
  const changeProgress = useCallback((patch: Partial<Progress>) => {
    if (patch.last) {
      const last = patch.last;
      if (!userRef.current) { setProgress(p => ({ ...p, last })); return; }
      execute({ path: '/api/state/position', method: 'PATCH', body: last, patch: p => ({ ...p, last }) }, true);
    } else execute({ path: '/api/state/preferences', method: 'PATCH', body: patch, patch: p => ({ ...p, ...patch }) });
  }, [execute]);
  const flag = (kind: 'bookmarks' | 'completed', id: string) => {
    const saved = !stateRef.current[kind].includes(id);
    execute({ path: `/api/state/${kind}/${encodeURIComponent(id)}`, method: 'PUT', body: { saved }, patch: p => ({ ...p, [kind]: saved ? Array.from(new Set([...p[kind], id])) : p[kind].filter(x => x !== id) }) });
  };
  const login = async (name: string, password: string) => {
    // Finish writes from any previous account before changing the server session.
    await queue.current;
    generation.current++;
    const session = await request<{ user: { username: string } }>('/api/auth/login', 'POST', { username: name, password });
    const state = await request<Progress>('/api/state', 'GET', undefined, session.user.username);
    setProgress(state); assignUser(session.user.username); setReady(true); setSaveError(''); setLoginOpen(false);
    const action = pending.current;
    pending.current = null;
    if (action) execute(action);
  };
  const logout = async () => {
    await queue.current;
    try {
      await request('/api/auth/logout', 'POST');
      generation.current++; assignUser(null); pending.current = null; setProgress(defaultProgress); setSaveError('');
    } catch (e) { setSaveError((e as Error).message); }
  };
  return { progress, username, ready, saveError, changeProgress,
    toggleCompleted: (id: string) => flag('completed', id), toggleBookmark: (id: string) => flag('bookmarks', id),
    openLogin: () => { pending.current = null; setLoginOpen(true); }, logout,
    dialog: loginOpen ? <LoginDialog login={login} close={() => { pending.current = null; setLoginOpen(false); }} /> : null };
}

function LoginDialog({ login, close }: { login: (name: string, password: string) => Promise<void>; close: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    const returnTo = document.activeElement as HTMLElement;
    dialog.current?.showModal();
    return () => { returnTo?.focus({ preventScroll: true }); };
  }, []);
  return <dialog ref={dialog} className="account-dialog" aria-labelledby="login-title" onCancel={e => { e.preventDefault(); if (!busy) close(); }}>
    <form onSubmit={async e => { e.preventDefault(); setBusy(true); setError(''); try { await login(name, password); } catch (e) { setError((e as Error).message); } finally { setBusy(false); } }}>
      <h2 id="login-title">Logga in</h2><p>Spara dina bokmärken, framsteg och läsinställningar på ditt konto.</p>
      <label className="form-label" htmlFor="login-name">Användarnamn</label><input id="login-name" className="form-control mb-3" autoComplete="username" autoFocus required maxLength={64} value={name} onChange={e => setName(e.target.value)} disabled={busy} />
      <label className="form-label" htmlFor="login-password">Lösenord</label><input id="login-password" className="form-control mb-3" type="password" autoComplete="current-password" required maxLength={1024} value={password} onChange={e => setPassword(e.target.value)} disabled={busy} />
      {error && <p className="alert alert-danger" role="alert">{error}</p>}
      <div className="d-flex gap-2 justify-content-end"><button className="btn btn-outline-secondary" type="button" disabled={busy} onClick={close}>Avbryt</button><button className="btn btn-primary" disabled={busy}>{busy ? 'Loggar in…' : 'Logga in'}</button></div>
    </form>
  </dialog>;
}
