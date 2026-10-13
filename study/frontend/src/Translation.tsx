import { Fragment } from 'react';

export type Vocabulary = { spans: { start: number; end: number; text: string }[]; lemma: string; pos: string; context_ru: string; general_ru: string };
export type TranslationRecord = { source_id: string; sv: string; ru: string; vocabulary: Vocabulary[] };
export type TranslationData = { available: boolean; language: string; records: Record<string, TranslationRecord> };
export type Selection = { record: TranslationRecord; word?: Vocabulary; index: number; surface: string };
type TextProps = { text: string; record?: TranslationRecord; selection: Selection | null; onSelect: (value: Selection, button: HTMLButtonElement) => void };

export function TranslationText({ text, record, selection, onSelect }: TextProps) {
  if (!record || record.sv !== text) return <>{text}</>;
  const chars = Array.from(text);
  const spans = record.vocabulary.flatMap((word, index) => word.spans.map(span => ({ ...span, word, index }))).sort((a, b) => a.start - b.start);
  const parts = [];
  const button = (surface: string, index: number, key: string, word?: Vocabulary, punctuation = '') => <span className="translation-token" key={key}><button
    type="button" key={key} className={`translation-word ${selection?.record.source_id === record.source_id && selection.index === index ? 'selected-word' : ''}`}
    aria-description="Visa rysk ordförklaring och meningsöversättning" aria-pressed={selection?.record.source_id === record.source_id && selection.index === index}
    aria-controls={selection ? 'translation-panel' : undefined} data-source-id={record.source_id} data-vocabulary-index={index}
    onClick={e => onSelect({ record, word, index, surface }, e.currentTarget)}>{surface}</button>{punctuation}</span>;
  const gap = (start: number, end: number) => {
    const raw = chars.slice(start, end).join('');
    let offset = 0;
    for (const match of raw.matchAll(/[\p{L}\p{M}\p{N}]+(?:[-’'][\p{L}\p{M}\p{N}]+)*/gu)) {
      const at = match.index!;
      parts.push(raw.slice(offset, at));
      // Negative indices identify unannotated words separately from vocabulary units.
      const punctuation = raw.slice(at + match[0].length).match(/^[.,;:!?…]+/)?.[0] || '';
      parts.push(button(match[0], -(start + Array.from(raw.slice(0, at)).length + 1), `gap-${start}-${at}`, undefined, punctuation));
      offset = at + match[0].length + punctuation.length;
    }
    parts.push(raw.slice(offset));
  };
  let offset = 0;
  for (const span of spans) {
    gap(offset, span.start);
    const punctuation = chars.slice(span.end).join('').match(/^[.,;:!?…]+/)?.[0] || '';
    parts.push(button(chars.slice(span.start, span.end).join(''), span.index, `word-${span.start}`, span.word, punctuation));
    offset = span.end + Array.from(punctuation).length;
  }
  gap(offset, chars.length);
  return <span className={selection?.record.source_id === record.source_id ? 'selected-sentence' : ''} data-sentence-id={record.source_id}>{parts.map((part, i) => <Fragment key={i}>{part}</Fragment>)}</span>;
}

const labels: Record<string, string> = { NOUN: 'Существительное', PROPN: 'Имя собственное', VERB: 'Глагол', ADJ: 'Прилагательное', ADV: 'Наречие', PRON: 'Местоимение', DET: 'Определитель', ADP: 'Предлог', AUX: 'Вспомогательный глагол', CCONJ: 'Сочинительный союз', SCONJ: 'Подчинительный союз', NUM: 'Числительное', PART: 'Частица', INTJ: 'Междометие', X: 'Другое' };

export function TranslationPanel({ selection, onClose }: { selection: Selection; onClose: () => void }) {
  const { record, word, surface } = selection;
  return <aside className="translation-panel" id="translation-panel" aria-label="Rysk översättning">
    <header className="translation-panel-header"><span><i className="bi bi-translate" aria-hidden="true" /> Svenska → Русский</span><button className="btn icon-button" onClick={onClose} aria-label="Stäng översättningen"><i className="bi bi-x-lg" aria-hidden="true" /></button></header>
    <div className="translation-panel-content" key={`${record.source_id}-${selection.index}`}>
      <div className="translation-announcement visually-hidden" role="status">{word ? `${word.lemma}: ${word.context_ru}` : `${surface}: meningsöversättning visas`}</div>
      <section className="word-meaning"><h2 lang="sv">{word?.lemma || surface}</h2>{word ? <><p className="context-meaning" lang="ru">{word.context_ru}</p></> : <p className="translation-muted">Ingen separat ordförklaring. Se meningen nedan.</p>}</section>
      <section className="sentence-meaning"><h3>Meningen på ryska</h3><p lang="ru">{record.ru}</p><details><summary>Svenskt original</summary><p lang="sv">{record.sv}</p></details></section>
      {word && <details className="dictionary-details"><summary>Ordbok</summary><p className="dictionary-meaning" lang="ru"><span>{labels[word.pos] || word.pos}</span>{word.general_ru}</p></details>}
    </div>
  </aside>;
}
