"""Protect collection indexing and deterministic chapter builds."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_collection
from build_pilot import build, dump_yaml, load_sources, read_yaml


class CollectionTests(unittest.TestCase):
    def test_index_keeps_existing_chapters_and_ignores_unbuilt_drafts(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'data'
            work = Path(directory) / 'work'
            documents = {'data/source.html': {'path': 'data/source.html', 'sha256': 'a',
                         'bytes': 1, 'extraction': 'fixture'}}
            for number in ['01', '05']:
                dump_yaml(dest / build_collection.chapter_path(number), {'title': number})
                dump_yaml(dest / f'metadata/{number}_provenance.yaml',
                          {'units': {number: {'source_path': 'data/source.html'}}})
            dump_yaml(work / 'chapters/02/selection.yaml', {'unfinished': True})
            with patch.object(build_collection, 'DEST', dest), patch.object(build_collection, 'WORK', work):
                build_collection.refresh_index(documents)
            manifest = read_yaml(dest / 'manifest.yaml')
            self.assertEqual([e['id'] for e in manifest['chapters']], ['hb-c01', 'hb-c05'])
            self.assertEqual(manifest['status'], 'in_progress')
            self.assertEqual(len(read_yaml(dest / 'metadata/sources.yaml')['sources']), 1)
            with patch.object(build_collection, 'DEST', dest), patch.object(build_collection, 'WORK', work):
                build_collection.refresh_index(documents, numbers=['05'])
            self.assertEqual([e['id'] for e in read_yaml(dest / 'manifest.yaml')['chapters']], ['hb-c05'])
            self.assertTrue((dest / build_collection.chapter_path('01')).exists())

    def test_every_built_chapter_reproduces_its_committed_text(self):
        manifest = read_yaml(build_collection.DEST / 'manifest.yaml')
        documents = load_sources()
        for entry in manifest['chapters']:
            number = f'{entry["order"]:02d}'
            selection, registry, _ = build_collection.inputs(number)
            chapter, _ = build(read_yaml(selection), copy.deepcopy(read_yaml(registry)), documents)
            with self.subTest(chapter=number):
                self.assertEqual(chapter, read_yaml(build_collection.DEST / entry['path']))


if __name__ == '__main__':
    unittest.main()
