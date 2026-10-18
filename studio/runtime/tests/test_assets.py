"""Regression checks for stale or mismatched narration assets."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import soundfile as sf
import yaml

MODULE = Path(__file__).resolve().parents[2] / 'tools/validate_assets.py'
SPEC = importlib.util.spec_from_file_location('validate_assets', MODULE)
assets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(assets)


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.episode = self.root / 'studio/episodes/test'
        self.episode.mkdir(parents=True)
        self.path = self.root / 'studio/media/test/one.wav'
        self.path.parent.mkdir(parents=True)
        sf.write(self.path, np.sin(np.arange(8000) / 10) * .2, 16000)
        self.relative = str(self.path.relative_to(self.root))
        self.script = dict(asset_requests=[dict(id='narration', kind='narration')], sentences=[dict(sentence_id='one', sv='Hej.', audio_path=self.relative)])
        self.entry = dict(path=self.relative, sentence_id='one', seconds=.5, tts_input='Hej.', sha256=hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.manifest = dict(assets=[dict(asset_id='narration', kind='narration', creator='Test', reuse_terms='Test', required_credits='Test', relevance_verification='Test', files=[self.entry])])

    def validate(self):
        (self.episode / 'script.yaml').write_text(yaml.safe_dump(self.script))
        (self.episode / 'assets.yaml').write_text(yaml.safe_dump(self.manifest))
        with patch.object(assets, 'ROOT', self.root):
            assets.validate('test')

    def test_valid_files(self):
        self.validate()

    def test_stereo_music_allowed_but_narration_remains_mono(self):
        music_path = self.path.with_name('music.wav')
        sf.write(music_path, np.full((8000, 2), .1), 16000)
        music = dict(self.manifest['assets'][0], asset_id='music', kind='music', files=[dict(
            path=str(music_path.relative_to(self.root)), seconds=.5,
            sha256=hashlib.sha256(music_path.read_bytes()).hexdigest())])
        self.script['asset_requests'].append(dict(id='music', kind='music'))
        self.manifest['assets'].append(music)
        self.validate()
        sf.write(self.path, np.full((8000, 2), .1), 16000)
        self.entry['sha256'] = hashlib.sha256(self.path.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'Invalid audio'):
            self.validate()

    def test_detects_changed_wav(self):
        self.path.write_bytes(self.path.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'Checksum mismatch'):
            self.validate()

    def test_rejects_old_speech_override(self):
        self.script['sentences'][0]['speech_override'] = {'text': 'Hej igen.'}
        with self.assertRaisesRegex(ValueError, 'input differs'):
            self.validate()

    def test_rejects_missing_sentence(self):
        self.script['sentences'].append(dict(sentence_id='two', sv='Hej igen.', audio_path=self.relative))
        with self.assertRaisesRegex(ValueError, 'coverage/order'):
            self.validate()

    def test_rejects_duplicate_asset_id(self):
        self.manifest['assets'].append(self.manifest['assets'][0].copy())
        with self.assertRaisesRegex(ValueError, 'IDs/kinds differ'):
            self.validate()


if __name__ == '__main__':
    unittest.main()
