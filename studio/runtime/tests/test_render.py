"""Check that rendering preserves text and schedules complete sentence audio."""
import importlib.util
import copy
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

SPEC = importlib.util.spec_from_file_location('render', Path(__file__).resolve().parents[2] / 'tools/render.py')
render = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render)
VERIFY_SPEC = importlib.util.spec_from_file_location('verify_render', Path(__file__).resolve().parents[2] / 'tools/verify_render.py')
verify_render = importlib.util.module_from_spec(VERIFY_SPEC)
VERIFY_SPEC.loader.exec_module(verify_render)


class RenderTests(unittest.TestCase):
    def test_cached_rgb_composite_matches_rgba_for_all_palette_cards_and_transitions(self):
        rng = np.random.default_rng(42)
        base = render.Image.fromarray(rng.integers(0, 256, size=(128, 192, 3), dtype=np.uint8))
        style = dict(zoom_start=1.06,zoom_end=1.219,pan_start=[.15,.15],pan_end=[.85,.85])
        for tint in ('#193b40','#442d30','#233c50','#243c32','#352e49'):
            card = render.Image.new('RGBA',(192,128),(0,0,0,0))
            draw = render.ImageDraw.Draw(card)
            draw.rectangle((71,11,185,119),fill=(*render.ImageColor.getrgb(tint),225))
            draw.ellipse((7,23,64,93),fill=(226,197,139,175))
            draw.line((4,4,170,101),fill=(250,243,232,255),width=3)
            previous = render.Image.new('RGBA',card.size,(32,71,59,228))
            with patch.object(render,'W',192),patch.object(render,'H',128):
                for transition in range(7):
                    overlay=card if transition==6 else render.Image.blend(previous,card,(transition+1)/6)
                    expected=render.Image.alpha_composite(render.background_frame(base,.37,style),overlay).convert('RGB')
                    actual=render.composite_rgb_frame(base,.37,style,overlay.convert('RGB'),overlay.getchannel('A'))
                    self.assertEqual(actual.tobytes(),expected.tobytes())

    def segmented_script(self):
        row = dict(sentence_id='one', sv='Ett första stycke. Ett andra stycke.',
                   ru='Первая часть. Вторая часть.', render_image=None,
                   text_highlights=[], audio_path='test.wav', pause_after_seconds=1.3,
                   display_segments=[dict(sv='Ett första stycke.', ru='Первая часть.',
                                          speech_offset_seconds=0),
                                     dict(sv='Ett andra stycke.', ru='Вторая часть.',
                                          speech_offset_seconds=4.25)])
        return dict(title_sv='Test', sentences=[row], render={'credits': []})

    def test_segments_preserve_one_full_audio_clip_lead_and_pause(self):
        script = self.segmented_script()
        with patch.object(render.sf, 'info', return_value=SimpleNamespace(duration=8.2)):
            timeline, frames = render.build_timeline(script)
        self.assertEqual(len(timeline), 2)
        item = timeline[1]
        self.assertAlmostEqual(item['speech_end_seconds']-item['speech_start_seconds'], 8.2)
        first, second = item['display_segments']
        self.assertEqual(first['start_frame'], item['start_frame'])
        self.assertEqual(first['start_frame']+first['frames'], second['start_frame'])
        self.assertEqual(second['start_frame'], round((item['speech_start_seconds']+4.25)*24))
        self.assertEqual(second['start_frame']+second['frames'], frames)
        self.assertGreaterEqual(frames/24-item['speech_end_seconds'], 1.3)
        for key in ('sv','ru'):
            self.assertEqual(' '.join(s[key] for s in item['display_segments']), script['sentences'][0][key])

    def test_segments_require_explicit_real_audio_boundaries(self):
        script = self.segmented_script()
        for offset in (None, -1, 0, .001, 8.2, float('nan')):
            with self.subTest(offset=offset):
                script['sentences'][0]['display_segments'][1]['speech_offset_seconds'] = offset
                with patch.object(render.sf, 'info', return_value=SimpleNamespace(duration=8.2)):
                    with self.assertRaisesRegex(ValueError, 'segment'):
                        render.build_timeline(script)

    def test_segments_cannot_drop_translation_or_reverse_boundaries(self):
        script = self.segmented_script()
        script['sentences'][0]['display_segments'][1]['ru'] = ''
        with patch.object(render.sf, 'info', return_value=SimpleNamespace(duration=8.2)):
            with self.assertRaisesRegex(ValueError, 'segment'):
                render.build_timeline(script)
        script = self.segmented_script()
        row = script['sentences'][0]
        row['sv'] += ' Slut.'
        row['ru'] += ' Конец.'
        row['display_segments'].append(dict(sv='Slut.', ru='Конец.', speech_offset_seconds=3))
        with patch.object(render.sf, 'info', return_value=SimpleNamespace(duration=8.2)):
            with self.assertRaisesRegex(ValueError, 'increase'):
                render.build_timeline(script)

    def test_each_segment_renders_its_own_aligned_language_pair(self):
        script = self.segmented_script()
        row = script['sentences'][0]
        for index, expected in enumerate(row['display_segments']):
            with patch.object(render, 'text_block', wraps=render.text_block) as text:
                render.make_card(script,dict(kind='sentence',sentence_id='one',segment_index=index),{'one':row},{})
            shown = [call.args[1] for call in text.call_args_list]
            self.assertEqual(shown,[expected['sv'],expected['ru']])

    def test_export_verifier_rejects_segment_gaps_and_changed_language_pair(self):
        script = self.segmented_script()
        with patch.object(render.sf, 'info', return_value=SimpleNamespace(duration=8.2)):
            timeline, _ = render.build_timeline(script)
        item = timeline[1]
        row = script['sentences'][0]
        for segment,timing in zip(row['display_segments'],item['display_segments']):
            segment.update(start_seconds=round(timing['start_frame']/24,6),
                           end_seconds=round((timing['start_frame']+timing['frames'])/24,6))
        self.assertEqual(verify_render.check_display_segments(row,item,24),2)
        altered = copy.deepcopy(item)
        altered['display_segments'][1]['start_frame'] += 1
        with self.assertRaisesRegex(ValueError,'gap'):
            verify_render.check_display_segments(row,altered,24)
        altered = copy.deepcopy(item)
        altered['display_segments'][1]['ru'] = 'Неверный перевод.'
        with self.assertRaisesRegex(ValueError,'differs from script'):
            verify_render.check_display_segments(row,altered,24)
        altered = copy.deepcopy(item)
        altered.pop('display_segments')
        with self.assertRaisesRegex(ValueError,'lost display segments'):
            verify_render.check_display_segments(row,altered,24)

    def test_soft_background_sampler_preserves_motion_and_colors(self):
        base = render.Image.linear_gradient('L').resize((2200, 1238)).convert('RGB')
        style = dict(zoom_start=1.06, zoom_end=1.219,
                     pan_start=[.15, .15], pan_end=[.85, .85])
        cubic = np.asarray(render.background_frame(base, .2, style), dtype=np.int16)
        linear = np.asarray(render.background_frame(base, .2, {**style, 'resampling': 'bilinear'}), dtype=np.int16)
        later = np.asarray(render.background_frame(base, .8, {**style, 'resampling': 'bilinear'}), dtype=np.int16)
        self.assertEqual(linear.shape, (1080, 1920, 4))
        self.assertLessEqual(np.abs(cubic - linear).max(), 2)
        self.assertGreater(np.abs(later - linear).mean(), 1)
        self.assertTrue(np.all(linear[:, :, 3] == 255))

    def test_episode_palette_colors_panel_and_progress(self):
        row = dict(sentence_id='one', sv='Finland.', ru='Финляндия.',
                   render_image=None, text_highlights=[])
        script = dict(title_sv='Finland', sentences=[row], render={'palette': {
            'background': '#202c40', 'highlight': '#d9b575', 'separator': '#46566d'}})
        try:
            render.configure_style(script)
            card, _ = render.make_card(script, {'kind': 'sentence', 'sentence_id': 'one'}, {'one': row}, {})
            self.assertEqual(card.getpixel((900, 500)), (32, 44, 64, 225))
            self.assertEqual(card.getpixel((930, 1002))[:3], (217, 181, 117))
            self.assertEqual(card.getpixel((100, 125))[:3], (70, 86, 109))
        finally:
            render.configure_style({})

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
