"""Helpers for explicit, source-reviewed chapter selections (no automatic curation)."""
from pathlib import Path
from build_pilot import WORK, load_sources, read_yaml, dump_yaml


class Editor:
    """Allocate stable editorial IDs once and preserve original article blocks."""

    def __init__(self, number):
        self.number = f'{int(number):02d}'
        self.identity = f'hb-c{self.number}'
        self.documents = load_sources()
        outline = read_yaml(WORK / 'outline.yaml')
        self.outline = next(c for c in outline['chapters'] if c['id'] == self.identity)
        self.selection = {'schema_version': 1, 'chapter_id': self.identity,
                          'title': self.outline['title'], 'language': 'sv', 'sections': []}
        self.serial = 0

    def allocate(self):
        self.serial += 1
        return f'{self.identity}-u{self.serial:04d}'

    def source(self, name):
        matches = [d for p, d in self.documents.items() if p == name or Path(p).stem == name]
        assert len(matches) == 1, (name, [d['path'] for d in matches])
        return matches[0]

    def section(self, slug, title):
        value = {'id': f'{self.identity}-{slug}', 'title': title, 'blocks': []}
        assert value['id'] not in [s['id'] for s in self.selection['sections']]
        self.selection['sections'].append(value)
        return value

    def add(self, section, source, numbers, reason=None):
        """Add explicitly chosen whole blocks; adjacent selected li become a list.

        This is an allocation helper, not a repeat-build interface. Keep generated
        selection IDs unchanged afterwards. Caller must read chosen blocks and
        preserve necessary context. DOM list ordering is detected from ancestors.
        """
        from bs4 import BeautifulSoup
        from extract_sources import ROOT
        doc = self.source(source)
        soup = BeautifulSoup((ROOT / doc['path']).read_text(encoding='utf-8'), 'html.parser')
        previous_list = None
        for number in numbers:
            bid = number if isinstance(number, str) else f'b{number:04d}'
            block = next(b for b in doc['blocks'] if b['id'] == bid)
            assert block['role'] not in {'activity', 'learning_objectives'}
            assert block['kind'] not in {'heading', 'table'}
            item = {'id': self.allocate(), 'kind': 'paragraph',
                    'source_path': doc['path'], 'source_block': bid}
            if reason:
                item['selection_reason'] = reason
            node = soup.select_one(block['locator'])
            parent = node.find_parent(['ol', 'ul']) if block['kind'] == 'li' else None
            parent_key = str(parent) if parent else None
            if block['kind'] == 'li':
                item['kind'] = 'item'
                if parent_key != previous_list or not section['blocks'] or section['blocks'][-1]['kind'] != 'list':
                    section['blocks'].append({'id': self.allocate(), 'kind': 'list',
                        'ordered': parent is not None and parent.name == 'ol', 'items': []})
                section['blocks'][-1]['items'].append(item)
            else:
                section['blocks'].append(item)
            previous_list = parent_key
        return section

    def excerpt(self, section, source, number, text, reason):
        """Select a literal contiguous passage with an explicit reason for filtering."""
        doc = self.source(source)
        block = next(b for b in doc['blocks'] if b['id'] == f'b{number:04d}')
        assert block['text'].count(text) == 1, text
        begin = block['text'].index(text)
        section['blocks'].append({'id': self.allocate(), 'kind': 'paragraph',
            'source_path': doc['path'], 'source_block': block['id'],
            'source_range': [begin, begin + len(text)], 'selection_reason': reason})

    def save(self):
        path = WORK / 'chapters' / self.number / 'selection.yaml'
        dump_yaml(path, self.selection)
        return path

    def audit(self, notes, topics, gaps=None, resolutions=None, **extra):
        """Create source audit; require source-specific reasons for every mapped unit.

        notes maps coverage source ID (or source path) to an editorial reason.
        Full block-level decisions can be supplied as primary_block_audit.
        """
        coverage = read_yaml(WORK / 'coverage.yaml')['sources']
        units = [u for s in self.selection['sections'] for b in s['blocks']
                 for u in b.get('items', [b])]
        selected_paths = {u['source_path'] for u in units}
        rows = []
        for candidate in coverage:
            if self.identity not in candidate['chapters'] and candidate['path'] not in selected_paths:
                continue
            path = candidate['path']
            selected = [u for u in units if u['source_path'] == path]
            if candidate['id'].startswith('textbook:'):
                selected = [u for u in selected if candidate['pdf_page_start'] <= u.get('pdf_page', 0) <= candidate['pdf_page_end_inclusive']]
                if not selected and self.identity not in candidate['chapters']:
                    continue
            note = notes.get(candidate['id'], notes.get(path))
            assert note, f'Missing source review reason for {candidate["id"]}'
            rows.append({'id': candidate['id'], 'path': path,
                         'decision': 'selected_with_omissions' if selected else 'reviewed_not_selected',
                         'selected_unit_ids': [u['id'] for u in selected], 'reason': note,
                         'remaining_destinations': [c for c in candidate['chapters'] if c != self.identity]})
        assert set(topics) == set(self.outline['topics'])
        value = {'schema_version': 1, 'chapter_id': self.identity, 'status': 'composed',
            'snapshot_policy': 'Fixed repository snapshots only; not independently verified current law.',
            'source_audit': rows, 'topic_coverage': topics, 'gaps': gaps or [],
            'resolutions': resolutions or [], **extra}
        dump_yaml(WORK / 'chapters' / self.number / 'audit.yaml', value)
        return value
