import { useEffect, useRef, useState } from 'react';

type Entry = { id: string; title: string };
type Chapter = Entry & { order: number; sections: Entry[] };

export function ReaderBreadcrumbs({ chapters, chapter, section }: { chapters: Chapter[]; chapter: Chapter; section: Entry }) {
  const [open, setOpen] = useState<'chapter' | 'section' | null>(null);
  const root = useRef<HTMLElement>(null);
  const chapterButton = useRef<HTMLButtonElement>(null);
  const sectionButton = useRef<HTMLButtonElement>(null);
  useEffect(() => { setOpen(null); }, [chapter.id, section.id]);
  useEffect(() => {
    if (!open) return;
    const outside = (event: PointerEvent) => { if (!root.current?.contains(event.target as Node)) setOpen(null); };
    document.addEventListener('pointerdown', outside);
    return () => document.removeEventListener('pointerdown', outside);
  }, [open]);
  const entries = open === 'chapter' ? chapters : chapter.sections;
  return <nav className="reader-breadcrumbs" aria-label="Läsnavigering" ref={root}
    onBlur={event => { if (!event.currentTarget.contains(event.relatedTarget)) setOpen(null); }}
    onKeyDown={event => {
      if (event.key === 'Escape' && open) {
        event.stopPropagation();
        (open === 'chapter' ? chapterButton : sectionButton).current?.focus();
        setOpen(null);
      }
    }}>
    <a className="breadcrumb-home" href="#/" aria-label="Alla kapitel" title="Alla kapitel"><i className="bi bi-grid" aria-hidden="true" /></a>
    <span className="breadcrumb-divider" aria-hidden="true">/</span>
    <button ref={chapterButton} className="breadcrumb-choice" aria-label="Välj kapitel" aria-expanded={open === 'chapter'} aria-controls="reader-location-choices" onClick={() => setOpen(open === 'chapter' ? null : 'chapter')}>
      <small>Kapitel {chapter.order}</small><span>{chapter.title}</span><i className="bi bi-chevron-down" aria-hidden="true" />
    </button>
    <span className="breadcrumb-divider" aria-hidden="true">/</span>
    <button ref={sectionButton} className="breadcrumb-choice" aria-label="Välj avsnitt" aria-expanded={open === 'section'} aria-controls="reader-location-choices" onClick={() => setOpen(open === 'section' ? null : 'section')}>
      <small>Avsnitt {chapter.sections.findIndex(s => s.id === section.id) + 1} av {chapter.sections.length}</small><span>{section.title}</span><i className="bi bi-chevron-down" aria-hidden="true" />
    </button>
    {open && <div className="breadcrumb-dropdown" id="reader-location-choices">
      <div className="breadcrumb-dropdown-heading">{open === 'chapter' ? 'Alla kapitel' : chapter.title}</div>
      <ul>{entries.map((entry, index) => <li key={entry.id}>
        <a href={open === 'chapter' ? `#/chapter/${entry.id}` : `#/chapter/${chapter.id}/${entry.id}`}
          aria-current={entry.id === (open === 'chapter' ? chapter.id : section.id) ? 'page' : undefined}
          onClick={() => { (open === 'chapter' ? chapterButton : sectionButton).current?.focus(); setOpen(null); }}>
          <span className="breadcrumb-number">{open === 'chapter' ? chapters[index].order : index + 1}</span><span>{entry.title}</span>
          {entry.id === (open === 'chapter' ? chapter.id : section.id) && <i className="bi bi-check2" aria-hidden="true" />}
        </a>
      </li>)}</ul>
    </div>}
  </nav>;
}
