import { Fragment, useEffect, useRef, useState } from 'react';
import { useAccount, type Progress } from './Account';
import { TranslationPanel, TranslationText, type Selection, type TranslationData } from './Translation';

type Unit = { id: string; text: string; sentences?: { id: string; start: number; end: number }[] };
type Block = Unit & { type: 'paragraph' | 'list'; ordered?: boolean; items?: Unit[] };
type Section = { id: string; title: string; blocks: Block[] };
type Chapter = { id: string; order: number; title: string; minutes: number; word_count: number; sections: Section[] };
type Summary = Omit<Chapter, 'sections'> & { sections: { id: string; title: string }[] };
type Library = { title: string; language: string; chapters: Summary[] };
type Passage = { chapter_id: string; chapter_title: string; section_id: string; section_title: string; unit_id: string; text: string; order: number };
type Source = { title: string; url?: string; group: string; page?: number; heading?: string };
type Attribution = { title: string; credit: string; url?: string; license: string; license_url?: string; changes: string };
type Route = { page: string; chapter?: string; section?: string; unit?: string; query?: string };
const themes = ['Land & språk', 'Historia', 'Kultur & traditioner', 'Demokrati', 'Rättigheter', 'Lag & rätt', 'Arbetsliv', 'Utbildning', 'Familj & barn', 'Hälsa & trygghet', 'Vardag & miljö', 'Integration'];
const icons = ['globe-europe-africa', 'hourglass-split', 'flower1', 'bank', 'shield-check', 'briefcase', 'building', 'mortarboard', 'people', 'heart-pulse', 'house', 'signpost-split'];

function parseRoute(): Route {
  const parts = location.hash.replace(/^#\/?/, '').split('/').map(p => { try { return decodeURIComponent(p); } catch { return p; } });
  return { page: parts[0] || 'home', chapter: parts[1], section: parts[2], unit: parts[3], query: parts[0] === 'search' ? parts[1] || '' : '' };
}
function chapterLink(chapter: string, section = '', unit = '') {
  return `#/chapter/${chapter}${section ? `/${section}` : ''}${unit ? `/${unit}` : ''}`;
}
async function api<T>(url: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(url, { signal });
  if (!response.ok) throw new Error(response.status === 404 ? 'Det du söker finns inte.' : 'Materialet kunde inte hämtas. Försök igen.');
  return response.json();
}
function Icon({ name, className = '' }: { name: string; className?: string }) {
  return <i className={`bi bi-${name} ${className}`} aria-hidden="true" />;
}
function Loading() { return <div className="loading-state" role="status"><span className="spinner-border spinner-border-sm me-3" />Hämtar materialet…</div>; }
function ErrorMessage({ message }: { message: string }) { return <div className="alert alert-danger" role="alert">{message} <button className="btn btn-sm btn-outline-danger ms-2" onClick={() => location.reload()}>Försök igen</button></div>; }
function Meter({ value }: { value: number }) { return <div className="progress" role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100} aria-label="Läsframsteg"><div className="progress-bar" style={{ width: `${value}%` }} /></div>; }
function Highlight({ text, query }: { text: string; query: string }) {
  const terms = query.trim().split(/\s+/).filter(Boolean);
  if (!terms.length) return <>{text}</>;
  const expression = new RegExp(`(${terms.map(term => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'gi');
  return <>{text.split(expression).map((part, index) => index % 2 ? <mark key={index}>{part}</mark> : part)}</>;
}

export default function App() {
  const [library, setLibrary] = useState<Library | null>(null);
  const [error, setError] = useState('');
  const [route, setRoute] = useState(parseRoute);
  const account = useAccount();
  const { progress, changeProgress, toggleCompleted, toggleBookmark } = account;
  const [menu, setMenu] = useState(false);
  const [query, setQuery] = useState('');
  const sidebarRef = useRef<HTMLElement>(null);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  useEffect(() => { const controller = new AbortController(); api<Library>('/api/library', controller.signal).then(setLibrary).catch(e => { if (e.name !== 'AbortError') setError(e.message); }); return () => controller.abort(); }, []);
  useEffect(() => { const listener = () => { setRoute(parseRoute()); setMenu(false); window.scrollTo(0, 0); }; window.addEventListener('hashchange', listener); return () => window.removeEventListener('hashchange', listener); }, []);
  useEffect(() => {
    if (!menu) return;
    const links = () => Array.from(sidebarRef.current?.querySelectorAll<HTMLAnchorElement>('a') || []);
    links()[0]?.focus();
    const keydown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMenu(false);
      if (e.key === 'Tab') {
        const items = links();
        const first = items[0], last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last?.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus(); }
      }
    };
    document.addEventListener('keydown', keydown);
    return () => { document.removeEventListener('keydown', keydown); menuButtonRef.current?.focus(); };
  }, [menu]);
  useEffect(() => { document.title = `${route.page === 'chapter' ? library?.chapters.find(c => c.id === route.chapter)?.title || 'Läs' : 'Samhällskunskap'} · Homebrew`; }, [route, library]);
  useEffect(() => {
    if (!account.ready || route.page !== 'chapter' || !library) return;
    const chapter = library.chapters.find(c => c.id === route.chapter);
    const section = chapter?.sections.find(s => s.id === route.section) || chapter?.sections[0];
    if (chapter && section) changeProgress({ last: { chapter: chapter.id, section: section.id } });
  }, [account.ready, account.username, route.page, route.chapter, route.section, library, changeProgress]);
  const allSections = library?.chapters.flatMap(c => c.sections) || [];
  const completed = allSections.filter(s => progress.completed.includes(s.id)).length;
  const overall = allSections.length ? Math.round(completed / allSections.length * 100) : 0;
  const openChapter = (chapter: Summary) => chapterLink(chapter.id, progress.last?.chapter === chapter.id && chapter.sections.some(s => s.id === progress.last?.section) ? progress.last.section : chapter.sections.find(s => !progress.completed.includes(s.id))?.id || chapter.sections[0].id);
  const resume = library?.chapters.find(c => c.id === progress.last?.chapter) || library?.chapters[0];

  return <div className={`app-shell ${route.page === 'chapter' ? 'reader-mode' : ''}`}>
    <a className="skip-link" href="#main-content" onClick={e => { e.preventDefault(); document.getElementById('main-content')?.focus(); }}>Till innehållet</a>
    {menu && <button className="sidebar-backdrop" aria-label="Stäng menyn" onClick={() => setMenu(false)} />}
    <aside ref={sidebarRef} className={`sidebar ${menu ? 'is-open' : ''}`} aria-label="Huvudmeny" onClick={e => { if ((e.target as HTMLElement).closest('a')) setMenu(false); }}>
      <a href="#/" className="brand"><span className="brand-mark"><Icon name="book" /></span><span>Homebrew<small>SAMHÄLLSKUNSKAP</small></span></a>
      <nav className="main-nav">
        <a href="#/" className={route.page === 'home' ? 'active' : ''}><Icon name="grid" />Översikt</a>
        <a href="#/saved" className={route.page === 'saved' ? 'active' : ''}><Icon name="bookmark" />Sparade texter{progress.bookmarks.length > 0 && <span className="nav-count">{progress.bookmarks.length}</span>}</a>
      </nav>
      <div className="sidebar-label">DINA KAPITEL <span>{library?.chapters.length || 12}</span></div>
      <nav className="chapter-nav" aria-label="Kapitel">
        {library?.chapters.map(c => <a key={c.id} href={openChapter(c)} className={route.chapter === c.id ? 'active' : ''} aria-current={route.chapter === c.id ? 'page' : undefined}>
          <span className="chapter-number">{String(c.order).padStart(2, '0')}</span><span>{themes[c.order - 1]}</span>
          {c.sections.every(s => progress.completed.includes(s.id)) && <Icon name="check-circle-fill" className="ms-auto" />}
        </a>)}
      </nav>
      <div className="sidebar-bottom"><div className="d-flex justify-content-between mb-2"><span>Din läsning</span><strong>{overall}%</strong></div><Meter value={overall} /><small>{completed} av {allSections.length || 187} avsnitt lästa</small><a href="#/about"><Icon name="info-circle" /> Om materialet</a></div>
    </aside>
    <div className="workspace">
      <header className="topbar">
        <button ref={menuButtonRef} className="btn icon-button mobile-menu" onClick={() => setMenu(true)} aria-label="Öppna menyn" aria-expanded={menu}><Icon name="list" /></button>
        <form className="search-form" role="search" onSubmit={event => { event.preventDefault(); if (query.trim().length >= 2) location.hash = `/search/${encodeURIComponent(query.trim())}`; }}>
          <Icon name="search" /><input className="form-control" type="search" aria-label="Sök i materialet" placeholder="Sök i alla kapitel…" value={query} minLength={2} maxLength={120} onChange={event => setQuery(event.target.value)} /><button className="search-submit" type="submit" aria-label="Sök"><Icon name="arrow-return-left" /></button>
        </form>
        <div className="topbar-tools"><div className="account-controls">{account.username ? <><span className="account-name">{account.username}</span><button className="btn btn-sm" onClick={() => void account.logout()}>Logga ut</button></> : <button className="btn btn-sm" onClick={account.openLogin} disabled={!account.ready}>Logga in</button>}</div><span className="language-label"><span className="finland-flag" /> Svenska</span><button className="btn icon-button" aria-label={progress.dark ? 'Aktivera ljust tema' : 'Aktivera mörkt tema'} onClick={() => changeProgress({ dark: !progress.dark })}><Icon name={progress.dark ? 'sun' : 'moon'} /></button></div>
      </header>
      <main id="main-content" tabIndex={-1}>
        {account.saveError && <div className="alert alert-warning m-3" role="alert">{account.saveError}</div>}
        {error ? <div className="page"><ErrorMessage message={error} /></div> : !library || !account.ready ? <Loading /> : route.page === 'chapter' ?
          <Reader key={route.chapter} library={library} route={route} progress={progress} changeProgress={changeProgress} toggleCompleted={toggleCompleted} toggleBookmark={toggleBookmark} /> :
          route.page === 'search' ? <Search key={route.query} query={route.query || ''} /> : route.page === 'saved' ? <Saved ids={progress.bookmarks} toggleBookmark={toggleBookmark} /> : route.page === 'about' ? <About /> :
          <div className="page overview">
            <div className="eyebrow"><span className="status-dot" /> DIN STUDIEPLATS</div>
            <section className="hero">
              <div><h1>Lär känna Finland.<br /><span>Ett kapitel i taget.</span></h1><p>Samhällskunskap inför medborgarskapsprovet.<br />Läs i din takt, spara det viktiga och följ dina framsteg.</p><a href={resume ? openChapter(resume) : '#/'} className="btn btn-primary hero-button"><Icon name="book" /> {progress.last ? 'Fortsätt läsa' : 'Börja läsa'} <Icon name="arrow-right" /></a><div className="hero-meta"><span><Icon name="collection" />12 kapitel</span><span><Icon name="translate" />På svenska</span><span><Icon name="check2-circle" />Din egen takt</span></div></div>
              <div className="book-illustration" aria-hidden="true"><div className="book-orbit orbit-one" /><div className="book-orbit orbit-two" /><div className="decor-star">✦</div><div className="illustrated-book"><span className="book-spine" /><div className="book-cover"><span className="finland-flag" /><small>HEMBYGGT LÄRMATERIAL</small><strong>Finland &<br />samhället</strong><span className="book-cover-line" /><span>En väg till förståelse.</span><Icon name="flower1" /></div></div><div className="book-caption"><Icon name="bookmark-check" /> Kunskap att bygga vidare på</div></div>
            </section>
            <section className="progress-summary"><span className="summary-icon"><Icon name="compass" /></span><div><strong>{completed ? 'Du är på väg. Fortsätt där du slutade.' : 'Din studieresa börjar här.'}</strong><span>{completed} av {allSections.length} avsnitt lästa · {account.username ? 'Dina framsteg sparas på ditt konto.' : 'Logga in för att spara dina framsteg.'}</span></div><div className="summary-meter"><strong>{overall}%</strong><Meter value={overall} /></div></section>
            <div className="section-heading"><div><h2>Utforska kapitlen</h2><p>Från Finlands historia till livet i vardagen.</p></div><span className="badge rounded-pill chapter-total">12 kapitel</span></div>
            <div className="row g-3 chapter-grid">{library.chapters.map(c => {
              const done = c.sections.filter(s => progress.completed.includes(s.id)).length;
              const percent = Math.round(done / c.sections.length * 100);
              return <div className="col-sm-6 col-xl-4" key={c.id}><a className="chapter-card card h-100" href={openChapter(c)}><div className="card-body"><div className="card-top"><span className={`chapter-icon tone-${(c.order - 1) % 4}`}><Icon name={icons[c.order - 1]} /></span><span className="card-number">{String(c.order).padStart(2, '0')}</span></div><h3>{c.title}</h3><p className="chapter-preview">{c.sections.slice(0, 3).map(s => s.title).join(' · ')}</p><div className="card-meta"><span>{c.sections.length} avsnitt</span><span><Icon name="clock" /> {c.minutes} min läsning</span></div><Meter value={percent} /><div className="card-bottom"><span>{done ? `${done} av ${c.sections.length} lästa` : 'Börja utforska'}</span><Icon name={percent === 100 ? 'check-circle' : 'arrow-up-right'} /></div></div></a></div>;
            })}</div>
            <footer className="page-footer"><span>Homebrew · Samhällskunskap inför medborgarskapsprovet</span><a href="#/about">Källor & om materialet <Icon name="arrow-up-right" /></a></footer>
          </div>}
      </main>
    </div>
    {account.dialog}
  </div>;
}

function Reader({ library, route, progress, changeProgress, toggleCompleted, toggleBookmark }: { library: Library; route: Route; progress: Progress; changeProgress: (p: Partial<Progress>) => void; toggleCompleted: (id: string) => void; toggleBookmark: (id: string) => void }) {
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [error, setError] = useState('');
  const [sources, setSources] = useState<Record<string, Source>>({});
  const sourceAttempted = useRef(false);
  const [translations, setTranslations] = useState<{ section: string; data: TranslationData } | null>(null);
  const [translationError, setTranslationError] = useState(false);
  const [translationAttempt, setTranslationAttempt] = useState(0);
  const [selection, setSelection] = useState<Selection | null>(null);
  const selectedButton = useRef<HTMLButtonElement | null>(null);
  const textPane = useRef<HTMLElement>(null);
  useEffect(() => { const controller = new AbortController(); api<Chapter>(`/api/chapters/${route.chapter}`, controller.signal).then(setChapter).catch(e => { if (e.name !== 'AbortError') setError(e.message); }); return () => controller.abort(); }, [route.chapter]);
  const section = chapter?.sections.find(s => s.id === route.section) || chapter?.sections[0];
  const sectionIndex = chapter?.sections.findIndex(s => s.id === section?.id) ?? 0;
  useEffect(() => {
    setSelection(null); setTranslations(null); setTranslationError(false);
    selectedButton.current = null;
    textPane.current?.scrollTo(0, 0);
    if (!chapter || !section) return;
    const controller = new AbortController();
    api<TranslationData>(`/api/chapters/${chapter.id}/sections/${section.id}/translation`, controller.signal)
      .then(data => setTranslations({ section: section.id, data }))
      .catch(e => { if (e.name !== 'AbortError') setTranslationError(true); });
    return () => controller.abort();
  }, [chapter?.id, section?.id, translationAttempt]);
  const closeTranslation = () => { setSelection(null); requestAnimationFrame(() => selectedButton.current?.focus({ preventScroll: true })); };
  useEffect(() => {
    if (!selection) return;
    const listener = (event: KeyboardEvent) => { if (event.key === 'Escape') closeTranslation(); };
    document.addEventListener('keydown', listener);
    return () => document.removeEventListener('keydown', listener);
  }, [selection]);
  useEffect(() => { if (route.unit && chapter && section) { const timer = window.setTimeout(() => document.getElementById(route.unit!)?.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100); return () => clearTimeout(timer); } }, [route.unit, chapter, section]);
  if (error) return <div className="page"><ErrorMessage message={error} /></div>;
  if (!chapter || !section) return <Loading />;
  const next = chapter.sections[sectionIndex + 1];
  const previous = chapter.sections[sectionIndex - 1];
  const nextChapter = library.chapters.find(c => c.order === chapter.order + 1);
  const done = progress.completed.includes(section.id);
  const sectionUnits = section.blocks.flatMap(b => b.items || [b]);
  const translation = translations?.section === section.id ? translations.data : null;
  const chooseWord = (value: Selection, button: HTMLButtonElement) => {
    selectedButton.current = button;
    setSelection(value);
    requestAnimationFrame(() => {
      if (!selection && window.matchMedia('(max-width: 700px) and (orientation: portrait)').matches) {
        button.closest('[data-sentence-id]')?.scrollIntoView({ block: 'start', inline: 'nearest' });
      }
      button.scrollIntoView({ block: 'nearest', inline: 'nearest' });
      document.querySelector('.translation-panel')?.scrollTo(0, 0);
    });
  };
  const translatedText = (id: string, text: string) => <TranslationText text={text} record={translation?.records[id]} selection={selection} onSelect={chooseWord} />;
  const unitText = (unit: Unit) => {
    if (!translation?.available || !unit.sentences) return unit.text;
    const chars = Array.from(unit.text);
    let end = 0;
    const result = unit.sentences.map(sentence => {
      const before = chars.slice(end, sentence.start).join('');
      end = sentence.end;
      return <Fragment key={sentence.id}>{before}{translatedText(sentence.id, chars.slice(sentence.start, sentence.end).join(''))}</Fragment>;
    });
    return <>{result}{chars.slice(end).join('')}</>;
  };
  const renderUnit = (unit: Unit) => <div className={`reader-unit ${route.unit === unit.id ? 'target-unit' : ''}`} id={unit.id} key={unit.id}><span>{unitText(unit)}</span><button className={`unit-bookmark btn icon-button ${progress.bookmarks.includes(unit.id) ? 'is-saved' : ''}`} aria-label={progress.bookmarks.includes(unit.id) ? 'Ta bort bokmärke' : 'Spara textstycke'} aria-pressed={progress.bookmarks.includes(unit.id)} onClick={() => toggleBookmark(unit.id)}><Icon name={progress.bookmarks.includes(unit.id) ? 'bookmark-fill' : 'bookmark-plus'} /></button></div>;
  return <div className="reader-page">
    <div className="reader-toolbar">
      <details className="reader-contents"><summary><Icon name="list-ol" /> Innehåll <span>{chapter.order} · {sectionIndex + 1}/{chapter.sections.length}</span></summary>
        <div className="reader-selectors">
          <label>Kapitel<select className="form-select" aria-label="Välj kapitel" value={chapter.id} onChange={e => { location.hash = chapterLink(e.target.value); }}>{library.chapters.map(c => <option key={c.id} value={c.id}>{c.order}. {c.title}</option>)}</select></label>
          <label>Avsnitt<select className="form-select" aria-label="Välj avsnitt" value={section.id} onChange={e => { location.hash = chapterLink(chapter.id, e.target.value); e.currentTarget.closest('details')?.removeAttribute('open'); }}>{chapter.sections.map((s, i) => <option key={s.id} value={s.id}>{i + 1}. {s.title}</option>)}</select></label>
        </div>
      </details>
      <div className="reading-tools" role="group" aria-label="Läsinställningar"><button className="btn" onClick={() => changeProgress({ serif: !progress.serif })} aria-label="Byt typsnitt" aria-pressed={progress.serif}>Aa</button><button className="btn" onClick={() => changeProgress({ size: Math.max(18, progress.size - 2) })} disabled={progress.size === 18} aria-label="Minska textstorleken">A−</button><button className="btn" onClick={() => changeProgress({ size: Math.min(24, progress.size + 2) })} disabled={progress.size === 24} aria-label="Öka textstorleken">A+</button></div>
    </div>
    <div className={`reader-layout ${selection ? 'has-translation' : ''}`}>
      <article className="reading-column" ref={textPane} aria-label="Svensk lästext" tabIndex={0}>
        <div className="reader-chapter-title">{translatedText(chapter.id, chapter.title)}</div>
        <h1>{translatedText(section.id, section.title)}</h1>
        <p className="reading-time"><Icon name="clock" /> {Math.max(1, Math.ceil(sectionUnits.reduce((n, u) => n + u.text.split(/\s+/).length, 0) / 200))} min <span>·</span>{done ? 'Läst' : `Avsnitt ${sectionIndex + 1} av ${chapter.sections.length}`}</p>
        <div className="translation-hint" role="status">{translationError ? <>Översättningen kunde inte hämtas. <button className="btn btn-sm btn-outline-primary" onClick={() => setTranslationAttempt(n => n + 1)}>Försök igen</button></> : !translation ? 'Hämtar språkstöd…' : translation.available ? <><Icon name="translate" /> Tryck på ett ord för rysk förklaring och mening.</> : 'Rysk översättning finns inte för det här avsnittet ännu.'}</div>
        <div className={`reader-text ${progress.serif ? 'serif' : ''}`} style={{ fontSize: progress.size }}>{section.blocks.map(block => block.type === 'paragraph' ? renderUnit(block) : block.ordered ? <ol key={block.id}>{block.items?.map(unit => <li key={unit.id}>{renderUnit(unit)}</li>)}</ol> : <ul key={block.id}>{block.items?.map(unit => <li key={unit.id}>{renderUnit(unit)}</li>)}</ul>)}</div>
        <div className="section-completion"><div><Icon name={done ? 'check-circle-fill' : 'check2-circle'} /><span>{done ? 'Det här avsnittet är läst.' : 'Klar med det här avsnittet?'}</span></div><button className={`btn ${done ? 'btn-outline-primary' : 'btn-primary'}`} aria-pressed={done} onClick={() => toggleCompleted(section.id)}>{done ? 'Markera som oläst' : 'Markera som läst'}</button></div>
        <div className="reading-navigation">{previous ? <a href={chapterLink(chapter.id, previous.id)}><Icon name="arrow-left" /><span><small>Föregående</small>{previous.title}</span></a> : <a href="#/"><Icon name="arrow-left" />Alla kapitel</a>}{next ? <a href={chapterLink(chapter.id, next.id)} className="next"><span><small>Nästa avsnitt</small>{next.title}</span><Icon name="arrow-right" /></a> : nextChapter ? <a href={chapterLink(nextChapter.id)} className="next"><span><small>Nästa kapitel</small>{nextChapter.title}</span><Icon name="arrow-right" /></a> : <a href="#/" className="next">Till översikten<Icon name="arrow-right" /></a>}</div>
        <details className="source-details" onToggle={e => { if (e.currentTarget.open && !sourceAttempted.current) { sourceAttempted.current = true; api<Record<string, Source>>(`/api/chapters/${chapter.id}/sources`).then(setSources).catch(() => { sourceAttempted.current = false; }); } }}><summary>Källor till avsnittet</summary><ul>{Object.keys(sources).length ? Array.from(new Map(sectionUnits.filter(u => sources[u.id]).map(u => { const s = sources[u.id]; return [JSON.stringify(s), s]; })).values()).map((s, i) => <li key={i}>{s.url ? <a href={s.url} target="_blank" rel="noreferrer">{s.title} <Icon name="box-arrow-up-right" /></a> : s.title}{s.page && ` · sida ${s.page}`}{s.heading && <small>{s.heading}</small>}</li>) : <li>Källorna hämtas. Stäng och öppna igen om hämtningen misslyckas.</li>}</ul><a href="#/about">Upphov och användningsvillkor</a></details>
      </article>
      {selection && <TranslationPanel selection={selection} onClose={closeTranslation} />}
    </div>
  </div>;
}

function PassageCard({ passage, query = '', remove }: { passage: Passage; query?: string; remove?: () => void }) {
  const start = query ? Math.max(0, passage.text.toLocaleLowerCase('sv').indexOf(query.trim().split(/\s+/)[0].toLocaleLowerCase('sv')) - 70) : 0;
  const excerpt = `${start ? '…' : ''}${passage.text.slice(start, start + 300)}${passage.text.length > start + 300 ? '…' : ''}`;
  return <article className="passage-card card"><div className="card-body"><div className="d-flex justify-content-between gap-3"><span className="eyebrow">KAPITEL {String(passage.order).padStart(2, '0')} · {passage.chapter_title}</span>{remove && <button className="btn icon-button" aria-label="Ta bort bokmärke" onClick={remove}><Icon name="bookmark-fill" /></button>}</div><a href={chapterLink(passage.chapter_id, passage.section_id, passage.unit_id)}><h2>{passage.section_title}</h2><p><Highlight text={excerpt} query={query} /></p><span className="passage-link">Läs i sitt sammanhang <Icon name="arrow-right" /></span></a></div></article>;
}
function Search({ query }: { query: string }) {
  const [result, setResult] = useState<{ total: number; results: Passage[] } | null>(null);
  const [error, setError] = useState('');
  const [loadingMore, setLoadingMore] = useState(false);
  useEffect(() => { setResult(null); setError(''); const controller = new AbortController(); api<{ total: number; results: Passage[] }>(`/api/search?q=${encodeURIComponent(query)}`, controller.signal).then(setResult).catch(e => { if (e.name !== 'AbortError') setError(e.message); }); return () => controller.abort(); }, [query]);
  return <div className="page results-page"><div className="eyebrow">SÖK I MATERIALET</div><h1>Resultat för ”{query}”</h1>{error ? <ErrorMessage message={error} /> : !result ? <Loading /> : <><p className="page-intro">{result.total} textstycken i materialet.</p>{result.results.length ? <div className="result-list">{result.results.map(p => <PassageCard key={p.unit_id} passage={p} query={query} />)}</div> : <div className="empty-state"><Icon name="search" /><h2>Inga träffar ännu</h2><p>Prova ett annat ord, till exempel ”rösträtt” eller ”Finland”.</p></div>}{result.results.length < result.total && <button className="btn btn-outline-primary mt-4" disabled={loadingMore} onClick={async () => { setLoadingMore(true); try { const more = await api<{ results: Passage[] }>(`/api/search?q=${encodeURIComponent(query)}&offset=${result.results.length}`); setResult(r => r ? { ...r, results: [...r.results, ...more.results] } : r); } catch (e) { setError((e as Error).message); } finally { setLoadingMore(false); } }}>{loadingMore ? 'Hämtar…' : 'Visa fler träffar'}</button>}</>}</div>;
}
function Saved({ ids, toggleBookmark }: { ids: string[]; toggleBookmark: (id: string) => void }) {
  const [passages, setPassages] = useState<Passage[]>([]);
  const [loading, setLoading] = useState(true);
  const [missing, setMissing] = useState<string[]>([]);
  useEffect(() => { const controller = new AbortController(); setLoading(true); Promise.all(ids.map(async id => { try { return await api<Passage>(`/api/passages/${id}`, controller.signal); } catch { return id; } })).then(values => { if (!controller.signal.aborted) { setPassages(values.filter((v): v is Passage => typeof v !== 'string')); setMissing(values.filter((v): v is string => typeof v === 'string')); setLoading(false); } }); return () => controller.abort(); }, [ids]);
  return <div className="page results-page"><div className="eyebrow">DIN EGEN SAMLING</div><h1>Sparade texter</h1><p className="page-intro">Det du vill återvända till. Dina bokmärken sparas på ditt konto.</p>{loading ? <Loading /> : ids.length ? <><div className="result-list">{passages.map(p => <PassageCard key={p.unit_id} passage={p} remove={() => toggleBookmark(p.unit_id)} />)}</div>{missing.map(id => <div className="alert alert-warning" key={id}>Textstycket kunde inte hämtas. <button className="btn btn-sm btn-outline-secondary" onClick={() => toggleBookmark(id)}>Ta bort bokmärket</button></div>)}</> : <div className="empty-state"><Icon name="bookmark-plus" /><h2>En plats för det viktiga</h2><p>Tryck på bokmärket bredvid ett textstycke när du läser.<br />Då hittar du det här.</p><a href="#/" className="btn btn-primary">Utforska kapitlen <Icon name="arrow-right" /></a></div>}</div>;
}
function About() {
  const [sources, setSources] = useState<Record<string, Attribution> | null>(null);
  const [error, setError] = useState('');
  useEffect(() => { const controller = new AbortController(); api<Record<string, Attribution>>('/api/sources', controller.signal).then(setSources).catch(e => { if (e.name !== 'AbortError') setError(e.message); }); return () => controller.abort(); }, []);
  return <div className="page about-page"><div className="eyebrow">OM HOMEBREW</div><h1>Kunskap med en källa.</h1><p className="page-intro">Samhällskunskap inför medborgarskapsprovet är en samling av utvalda texter från tre befintliga läromaterial.</p><div className="about-intro"><h2>Så använder du materialet</h2><p>Läs kapitlen i valfri ordning. Markera avsnitt som lästa och spara stycken du vill gå tillbaka till. Logga in för att spara dina framsteg, bokmärken och läsinställningar på ditt konto och använda dem på flera enheter.</p><p>Samlingen återger arkiverade källor. Lagar, belopp och myndighetsuppgifter kan ha ändrats. Materialet är ett fristående studiestöd och ingen officiell frågebank.</p></div><h2 className="mb-4">Källor och upphov</h2>{error ? <ErrorMessage message={error} /> : !sources ? <Loading /> : Object.entries(sources).map(([key, source]) => <section className="attribution-card card" key={key}><div className="card-body"><div className="eyebrow">{key === 'orientation' ? 'SAMHÄLLSORIENTERING PÅ WEBBEN' : key === 'textbook' ? 'LÄROBOK' : 'INFORMATION OM FINLAND'}</div><h3>{source.title}</h3><p>{source.credit}</p>{source.url && <a href={source.url} target="_blank" rel="noreferrer">Besök originalkällan <Icon name="box-arrow-up-right" /></a>}<details><summary>Originalets användningsvillkor</summary><p>{source.license}</p>{source.license_url && <a href={source.license_url} target="_blank" rel="noreferrer">{source.license_url}</a>}<p className="mt-2">{source.changes}</p></details></div></section>)}</div>;
}
