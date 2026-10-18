"""Check that rendering preserves text and schedules complete sentence audio."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

SPEC = importlib.util.spec_from_file_location('render', Path(__file__).resolve().parents[2] / 'tools/render.py')
render = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render)


class RenderTests(unittest.TestCase):
    def test_long_title_and_large_sentence_count_fit(self):
        title = 'Landskap, regioner och städer'
        self.assertLessEqual(render.fitted_font(title, 94, 1640, True).getlength(title), 1640)
        rows = [dict(sentence_id=str(i), sv='Finland.', ru='Финляндия.',
                     render_image=None, text_highlights=[]) for i in range(54)]
        card, _ = render.make_card(dict(title_sv=title, sentences=rows),
                                   dict(kind='sentence', sentence_id='53'),
                                   {r['sentence_id']: r for r in rows}, {})
        self.assertEqual(card.getpixel((1840, 1002))[3], 0)
        self.assertGreater(card.getpixel((1820, 1002))[3], 0)

    def test_explicit_music_loop_preserves_level_and_duration(self):
        music = np.full((100, 2), .25, dtype=np.float32)
        with patch.object(render, 'RATE', 10):
            result = render.loop_music(music, 305, 2)
            with self.assertRaisesRegex(ValueError, 'crossfade'):
                render.loop_music(music, 305, 6)
        self.assertEqual(result.shape, (305, 2))
        np.testing.assert_allclose(result, .25, atol=1e-7)

    def test_long_video_background_moves_at_opening_and_turns_smoothly(self):
        style = dict(zoom_start=1.06, zoom_end=1.219, motion_cycles=3,
                     pan_start=[.15, .15], pan_end=[.85, .85])
        crops = [render.background_extent((2200, 1238), n / 10080, style)
                 for n in range(10081)]
        self.assertGreater(crops[120][0] - crops[0][0], 10)
        self.assertLess(max(max(abs(a-b) for a,b in zip(x,y))
                            for x,y in zip(crops,crops[1:])), .5)
        self.assertAlmostEqual(crops[0][0], crops[-1][0])

    def test_wrap_preserves_both_languages(self):
        for text in ['Finlands areal är 338 432 km².', 'Площадь Финляндии составляет 338 432 км².']:
            self.assertEqual(' '.join(render.wrap(text, render.font(40), 330)), text)

    def test_overlong_word_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Word exceeds'):
            render.wrap('naturförhållandena', render.font(48), 20)

    def test_background_motion_is_subpixel_and_continuous(self):
        style = {'zoom_start': 1.06, 'zoom_end': 1.219, 'pan_start': [.15, .15], 'pan_end': [.85, .85]}
        crops = [render.background_extent((2200, 1238), frame / 3400, style) for frame in range(3401)]
        for before, after in zip(crops, crops[1:]):
            self.assertLess(max(abs(a - b) for a, b in zip(before, after)), .25)
            self.assertGreaterEqual(after[0], before[0])
        self.assertNotEqual(crops[1000][0], round(crops[1000][0]))
        self.assertNotEqual(crops[1000], crops[1001])
        self.assertGreater(crops[-1][0] - crops[0][0], 250)
        self.assertGreater(crops[-1][1] - crops[0][1], 140)
        self.assertAlmostEqual((crops[0][2] - crops[0][0]) / (crops[-1][2] - crops[-1][0]), 1.15)
        self.assertGreater(crops[240][0] - crops[0][0], 8)

    def test_missing_useful_image_leaves_transparent_foreground(self):
        row = dict(sentence_id='one', sv='Finland.', ru='Финляндия.', render_image=None, text_highlights=[])
        script = dict(title_sv='Finland', sentences=[row])
        card, photo = render.make_card(script, {'kind': 'sentence', 'sentence_id': 'one'}, {'one': row}, {})
        self.assertEqual(card.getpixel((400, 500))[3], 0)
        self.assertGreater(card.getpixel((900, 500))[3], 0)
        self.assertIsNone(photo)

    def test_measured_audio_lead_and_pause_are_preserved(self):
        rows = [dict(sentence_id=str(i), audio_path='test.wav', pause_after_seconds=1.3) for i in range(2)]
        with patch.object(render.sf, 'info', return_value=SimpleNamespace(duration=3.017)):
            timeline, frames = render.build_timeline(dict(sentences=rows, render={'credits': [None, None]}))
        self.assertEqual(timeline[0]['frames'], 72)
        for item in timeline[1:3]:
            self.assertAlmostEqual(item['speech_start_seconds'] - item['start_frame'] / 24, .25)
            self.assertAlmostEqual(item['speech_end_seconds'] - item['speech_start_seconds'], 3.017)
            self.assertGreaterEqual((item['start_frame'] + item['frames']) / 24 - item['speech_end_seconds'], 1.3)
        for previous, following in zip(timeline, timeline[1:]):
            self.assertEqual(previous['start_frame'] + previous['frames'], following['start_frame'])
        self.assertEqual(frames, sum(item['frames'] for item in timeline))


if __name__ == '__main__':
    unittest.main()
