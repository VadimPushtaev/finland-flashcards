import { useEffect, useRef, useState } from 'react';
import { TranslationPanel, TranslationText, type Selection, type TranslationData } from './Translation';

type Chapter = { id: string; order: number; title: string; total: number; new: number; due: number };
type Card = { id: string; chapter_id: string; topic: string; question: string; options: string[] };
type Overview = { chapters: Chapter[]; desired_retention: number };
type Stats = { total: number; correct: number; incorrect: number; with_translation: number;
  grades: Record<string, number>; breakdown: Record<string, number>;
  events: { reviewed_at: string; correct: number; translation_used: number;
    suggested_grade: number; final_grade: number; kind: string }[] };
type Check = { correct: boolean; correct_option: number };
type Extra = { cards: Card[]; fallback: Card[]; count: number; fallback_count: number };

const grades = ['Again', 'Hard', 'Good', 'Easy'];
const noTranslation: TranslationData = { available: false, language: 'ru', records: {} };

async function call<T>(path: string, method = 'GET', body?: object, username?: string): Promise<T> {
  const headers: Record<string, string> = method === 'GET' ? {} :
    { 'Content-Type': 'application/json', 'X-Study-Request': '1' };
  if (username) headers['X-Study-User'] = username;
  const response = await fetch(path, { method, headers, credentials: 'same-origin',
    body: body === undefined ? undefined : JSON.stringify(body) });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(typeof data.detail === 'string' ? data.detail : 'Kunde inte hämta information.');
  }
  return response.json() as Promise<T>;
}
function shuffled<T>(items: T[]): T[] {
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

export function Practice({ chapterId, username, openLogin }: {
  chapterId?: string; username: string | null; openLogin: () => void;
}) {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [queue, setQueue] = useState<Card[]>([]);
  const [current, setCurrent] = useState<Card | null>(null);
  const [started, setStarted] = useState(false);
  const [completed, setCompleted] = useState<string[]>([]);
  const [choice, setChoice] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<Check | null>(null);
  const [grade, setGrade] = useState(3);
  const [hint, setHint] = useState(false);
  const [kind, setKind] = useState('normal');
  const [eventId, setEventId] = useState('');
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [retention, setRetention] = useState(0.9);
  const [extraThreshold, setExtraThreshold] = useState(0.9);
  const [extra, setExtra] = useState<Extra | null>(null);
  const [extraOpen, setExtraOpen] = useState(false);
  const [stats, setStats] = useState<Stats | null>(null);
  const [statsOpen, setStatsOpen] = useState(false);
  const [translations, setTranslations] = useState<TranslationData>(noTranslation);
  const [selection, setSelection] = useState<Selection | null>(null);
  const lastWord = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (!username) { setLoading(false); return; }
    let active = true;
    setLoading(true);
    call<Overview>('/api/practice/overview', 'GET', undefined, username).then(result => {
      if (!active) return;
      setOverview(result); setRetention(result.desired_retention);
      setExtraThreshold(result.desired_retention);
    }).catch(e => { if (active) setError((e as Error).message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [username]);

  useEffect(() => {
    if (!current) { setTranslations(noTranslation); setSelection(null); return; }
    let active = true;
    setTranslations(noTranslation); setSelection(null); setStats(null); setStatsOpen(false);
    call<TranslationData>('/api/practice/chapters/' + current.chapter_id +
      '/cards/' + current.id + '/translation').then(data => {
      if (active) setTranslations(data);
    }).catch(() => { if (active) setTranslations(noTranslation); });
    return () => { active = false; };
  }, [current?.id]);

  useEffect(() => {
    if (!extraOpen || !chapterId || !username) return;
    let active = true;
    const timer = window.setTimeout(() => call<Extra>(
      '/api/practice/chapters/' + chapterId + '/extra', 'POST',
      { threshold: extraThreshold, excluded_ids: [...new Set(completed)] }, username
    ).then(result => { if (active) setExtra(result); })
      .catch(e => { if (active) setError((e as Error).message); }), 150);
    return () => { active = false; window.clearTimeout(timer); };
  }, [extraOpen, chapterId, extraThreshold, username, completed.length]);

  const show = (card: Card, reason: string) => {
    setCurrent(card); setKind(reason); setFeedback(null); setChoice(null);
    setHint(false); setGrade(3); setEventId(crypto.randomUUID().replaceAll('-', ''));
  };
  const start = async () => {
    if (!chapterId || !username) return;
    setBusy(true); setError('');
    try {
      const result = await call<{cards: Card[]}>(
        '/api/practice/chapters/' + chapterId + '/queue', 'GET', undefined, username);
      const cards = shuffled(result.cards);
      setQueue(cards.slice(1)); setCompleted([]); setStarted(true);
      if (cards[0]) show(cards[0], 'normal');
      else setCurrent(null);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  };
  const answer = async (option: number) => {
    if (!current || !username || choice !== null || busy) return;
    setChoice(option); setError('');
    try {
      const result = await call<Check>('/api/practice/chapters/' + current.chapter_id +
        '/cards/' + current.id + '/check', 'POST', { option }, username);
      setFeedback(result);
      setGrade(result.correct ? (hint ? 2 : 3) : 1);
    } catch (e) { setChoice(null); setError((e as Error).message); }
  };
  const next = async () => {
    if (!current || !feedback || choice === null || !username || busy) return;
    setBusy(true); setError('');
    try {
      await call('/api/practice/chapters/' + current.chapter_id + '/review', 'POST',
        { event_id: eventId, card_id: current.id, option: choice, grade,
          translation_used: hint, kind }, username);
      setCompleted(previous => [...previous, current.id]);
      const remaining = [...queue];
      if (grade === 1) remaining.splice(Math.min(3, remaining.length), 0, current);
      const following = remaining.shift();
      setQueue(remaining);
      if (following) show(following, following.id === current.id ||
        completed.includes(following.id) ? 'retry' : kind === 'extra' ? 'extra' : 'normal');
      else { setCurrent(null); setExtra(null); setExtraOpen(false); }
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  };
  const saveRetention = async () => {
    if (!username || busy) return;
    setBusy(true); setError('');
    try {
      await call('/api/practice/settings', 'PATCH', { desired_retention: retention }, username);
      setOverview(old => old ? { ...old, desired_retention: retention } : old);
      setExtraThreshold(retention);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  };
  const startExtra = (cards: Card[]) => {
    const sorted = shuffled(cards);
    setQueue(sorted.slice(1)); setExtraOpen(false); setExtra(null);
    if (sorted[0]) show(sorted[0], 'extra');
  };
  const chooseWord = (value: Selection, button: HTMLButtonElement) => {
    lastWord.current = button; setSelection(value);
    if (choice === null) setHint(true);
  };
  const closeTranslation = () => { setSelection(null); lastWord.current?.focus({preventScroll: true}); };
  const translated = (key: string, text: string) => <TranslationText text={text}
    record={translations.records[key]} selection={selection} onSelect={chooseWord} />;
  const showStats = async () => {
    if (!current || !username) return;
    setStatsOpen(!statsOpen);
    if (!statsOpen) {
      try { setStats(await call<Stats>('/api/practice/cards/' + current.id + '/stats')); }
      catch (e) { setError((e as Error).message); }
    }
  };
  if (!username) return <div className="page practice-page"><h1>Öva med kort</h1>
    <p>Logga in för att spara dina svar och följa dina framsteg.</p>
    <button className="btn btn-primary" onClick={openLogin}>Logga in</button></div>;
  const chapter = overview?.chapters.find(c => c.id === chapterId);
  return <div className="page practice-page">
    <div className="eyebrow">HOME­BREW · ÖVNING</div>
    {chapterId && <a className="practice-back" href="#/practice">← Alla kapitel</a>}
    <h1>{chapter?.title || 'Öva med kort'}</h1>
    {error && <div className="alert alert-danger" role="alert">{error}</div>}
    {loading ? <div role="status">Hämtar kort…</div> : !chapterId ? <>
      <p className="page-intro">Välj ett kapitel. Alla nya och aktuella kort ingår, utan dagliga gränser.</p>
      <section className="card practice-settings"><div className="card-body">
        <h2>Önskad minnesnivå</h2>
        <label htmlFor="retention">FSRS: {Math.round(retention * 100)}%</label>
        <input id="retention" type="range" min="70" max="99" step="1"
          value={Math.round(retention * 100)}
          onChange={e => setRetention(Number(e.target.value) / 100)} />
        <p className="small text-muted">Högre nivå ger tätare repetitioner. Ändringen gäller framtida svar.</p>
        <button className="btn btn-outline-primary" disabled={busy ||
          retention === overview?.desired_retention} onClick={() => void saveRetention()}>
          Spara inställning</button>
      </div></section>
      <div className="row g-3 mt-3">{overview?.chapters.map(c => <div className="col-sm-6 col-xl-4" key={c.id}>
        <a href={'#/practice/' + c.id} className="card practice-chapter h-100">
          <div className="card-body"><span className="eyebrow">KAPITEL {c.order}</span>
            <h2>{c.title}</h2><strong>{c.new + c.due} kort att öva</strong>
            <p className="small text-muted mb-0">{c.new} nya · {c.due} att repetera · {c.total} totalt</p>
          </div></a></div>)}</div>
    </> : !started ? <div className="card practice-start"><div className="card-body">
      <p>{chapter ? chapter.new + chapter.due : ''} kort att öva.</p>
      <button className="btn btn-primary" disabled={busy} onClick={() => void start()}>Starta övningen</button>
    </div></div> : current ? <div className="practice-workspace">
      <div className="practice-status"><span>{completed.length} sparade svar</span>
        <span>{queue.length + 1} kort kvar</span></div>
      <article className="card practice-question"><div className="card-body">
        <div className="eyebrow">{current.topic}</div>
        <h2 lang="sv">{translated(current.id + ':q', current.question)}</h2>
        <div className="practice-options">{current.options.map((option, i) => {
          const record = translations.records[current.id + ':a' + i];
          const cls = feedback && i === feedback.correct_option ? 'is-correct' :
            feedback && choice === i ? 'is-wrong' : '';
          return <div key={i} className={'practice-option ' + cls}>
            <button className="btn practice-answer" disabled={choice !== null} aria-pressed={choice === i}
              onClick={() => void answer(i)}>
              <span className="practice-option-letter">{String.fromCharCode(65 + i)}</span>
              <span lang="sv">{record ? 'Välj det här svaret' : option}</span>
            </button>
            {record && <div className="practice-option-translation" lang="sv">
              {translated(current.id + ':a' + i, option)}</div>}
          </div>;
        })}</div>
        {feedback && <div className={'practice-feedback ' +
          (feedback.correct ? 'is-correct' : 'is-wrong')} role="status">
          {feedback.correct ? 'Rätt svar!' :
            'Inte riktigt. Rätt svar: ' + current.options[feedback.correct_option]}
        </div>}
        {feedback && <section className="practice-grading">
          <p>Bedömning (du kan ändra den)</p>
          <div className="practice-grades" role="group" aria-label="FSRS-bedömning">
            {grades.map((name, i) => <button key={name}
              className={'btn ' + (grade === i + 1 ? 'btn-primary' : 'btn-outline-secondary')}
              aria-pressed={grade === i + 1} onClick={() => setGrade(i + 1)}>{name}</button>)}
          </div>
          <div className="practice-actions">
            <button className="btn btn-link" onClick={() => void showStats()}>
              {statsOpen ? 'Dölj statistik' : 'Visa statistik'}</button>
            <button className="btn btn-primary" disabled={busy} onClick={() => void next()}>
              {busy ? 'Sparar…' : 'Nästa →'}</button>
          </div>
        </section>}
      </div></article>
      {statsOpen && <section className="card practice-stats"><div className="card-body">
        <h3>Historik för det här kortet</h3>
        {!stats ? 'Hämtar statistik…' : <>
          <p>{stats.total} svar · {stats.correct} rätt · {stats.incorrect} fel ·
            {stats.with_translation} med översättning</p>
          <div className="practice-stat-grid">
            {Object.entries(stats.breakdown).map(([key, value]) =>
              <div key={key}><strong>{value}</strong><span>{key.replaceAll('_', ' ')}</span></div>)}
            {Object.entries(stats.grades).map(([key, value]) =>
              <div key={key}><strong>{value}</strong><span>{key}</span></div>)}
          </div>
          <ol className="practice-history">{stats.events.map((item, i) => <li key={i}>
            {new Date(item.reviewed_at).toLocaleString()} · {item.correct ? 'Rätt' : 'Fel'} ·
            {item.translation_used ? ' med översättning' : ' utan översättning'} ·
            {grades[item.final_grade - 1]}
            {item.suggested_grade !== item.final_grade ? ' (ändrad)' : ''}
          </li>)}</ol>
        </>}
      </div></section>}
      {selection && <TranslationPanel selection={selection} onClose={closeTranslation} />}
    </div> : <section className="card practice-finished"><div className="card-body">
      <h2>Klart för den här gången!</h2>
      <p>Du har gått igenom korten som var redo att övas.</p>
      <button className="btn btn-outline-primary"
        onClick={() => { setExtraOpen(!extraOpen); setExtra(null); }}>Jag vill öva mer</button>
      {extraOpen && <div className="practice-extra">
        <label htmlFor="extra-threshold">Tillfällig extra övning: {Math.round(extraThreshold * 100)}%</label>
        <input id="extra-threshold" type="range" min={Math.round((overview?.desired_retention || 0.9) * 100)}
          max="99" step="1" value={Math.round(extraThreshold * 100)}
          onChange={e => setExtraThreshold(Number(e.target.value) / 100)} />
        <p className="small text-muted">Denna gräns ändrar inte din vanliga inställning.</p>
        {extra ? <>
          <p>{extra.count} extra kort tillgängliga.</p>
          {extra.count > 0 && <button className="btn btn-primary"
            onClick={() => startExtra(extra.cards)}>Öva {extra.count} kort</button>}
          {extra.count === 0 && extra.fallback_count > 0 && <>
            <p>Inga kort matchade. Du kan repetera de närmast schemalagda korten.</p>
            <button className="btn btn-primary" onClick={() => startExtra(extra.fallback)}>
              Öva nästa {extra.fallback_count} kort</button>
          </>}
          {!extra.count && !extra.fallback_count &&
            <p>Inga fler kort är tillgängliga just nu.</p>}
        </> : <p>Letar efter extra kort…</p>}
      </div>}
    </div></section>}
  </div>;
}
