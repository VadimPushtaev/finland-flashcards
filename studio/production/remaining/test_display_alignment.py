"""Exercise ambiguity,spoken order and dual-pass timing safeguards."""
import unittest

from align_display_segments import boundary,agreed_boundary


def words(text,shift=0):
    return [dict(word=w,start=i*.4+shift,end=i*.4+.3+shift,probability=.95)
            for i,w in enumerate(text.split())]


class AlignmentChecks(unittest.TestCase):
    def test_measured_gap_and_two_pass_agreement(self):
        a=words('barn och unga men som behöver hjälp')
        b=words('barn och unga men som behöver hjälp',.04)
        result=agreed_boundary('barn och unga','men som behöver hjälp',a,b,4)
        self.assertAlmostEqual(result['offset_seconds'],1.17)

    def test_ambiguous_phrase_must_not_choose_an_arbitrary_occurrence(self):
        a=words('barn och unga men som behöver hjälp barn och unga')
        with self.assertRaisesRegex(ValueError,'unambiguous'):
            boundary('barn och unga','men som behöver hjälp',a,5)

    def test_prompt_must_not_move_boundary_without_review(self):
        a=words('barn och unga men som behöver hjälp')
        b=words('barn och unga men som behöver hjälp',.3)
        with self.assertRaisesRegex(ValueError,'disagree'):
            agreed_boundary('barn och unga','men som behöver hjälp',a,b,5)

    def test_low_confidence_anchor_requires_review(self):
        a=words('barn och unga men som behöver hjälp');a[3]['probability']=.2
        with self.assertRaisesRegex(ValueError,'Low-confidence'):
            boundary('barn och unga','men som behöver hjälp',a,4)


if __name__=='__main__':unittest.main()
