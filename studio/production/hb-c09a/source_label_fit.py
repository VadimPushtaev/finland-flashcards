"""Explicit Swedish compound hyphenation for original picture captions.

Raw labels remain exact source substrings. Only their typographic line breaks
receive conventional visible hyphens; no narration or bilingual text is edited.
"""
from PIL import ImageFont

COMPOUNDS = {
    'begravningskostnaderna': 'begravnings|kostnaderna',
    'arbetspensionsförsäkring': 'arbetspensions|försäkring',
    'graviditetspenningperioden': 'graviditets|penningperioden',
    'barnskyddsmyndigheterna': 'barnskydds|myndigheterna',
    'barnskyddsmyndigheten': 'barnskydds|myndigheten',
    'barnskyddsmyndigheter': 'barnskydds|myndigheter',
    'barnskyddsanmälan': 'barnskydds|anmälan',
    'barnskyddsarbetet': 'barnskydds|arbetet',
    'omhändertagande': 'omhänder|tagande',
    'omhändertagandet': 'omhänder|tagandet',
    'begravningsplatserna': 'begravnings|platserna',
    'begravningstillstånd': 'begravnings|tillstånd',
    'begravningsbyråer': 'begravnings|byråer',
    'begravningsbyråerna': 'begravnings|byråerna',
    'begravningsplatser': 'begravnings|platser',
    'begravningsbidrag': 'begravnings|bidrag',
    'arbetspensionssystemet': 'arbetspensions|systemet',
    'befolkningsdatasystemet': 'befolkningsdata|systemet',
    'livförsäkringsärenden': 'livförsäkrings|ärenden',
    'undervisningsbruk': 'undervisnings|bruk',
    'familjehemsförälder': 'familjehems|förälder',
    'familjehemsföräldrarna': 'familjehems|föräldrarna',
    'fertilitetsbehandling': 'fertilitets|behandling',
    'fertilitetsbehandlingar': 'fertilitets|behandlingar',
    'fertilitetsbehandlingen': 'fertilitets|behandlingen',
    'ensamförsörjartillägg': 'ensamförsörjar|tillägg',
    'förlossningsdatumet': 'förlossnings|datumet',
    'graviditetspenning': 'graviditets|penning',
    'familjemedlemmarna': 'familje|medlemmarna',
    'barnatillsyningsmannen': 'barnatillsynings|mannen',
    'efternamnskombination': 'efternamns|kombination',
    'jordbruksdominerade': 'jordbruks|dominerade',
    'gemenskapsorienterade': 'gemenskaps|orienterade',
    'arbetsfördelningen': 'arbets|fördelningen',
    'jämställdhetsfråga': 'jämställdhets|fråga',
    'småbarnspedagogiken': 'småbarns|pedagogiken',
    'familjeförberedelsekurs': 'familje|förberedelsekurs',
    'moderskapsunderstöd': 'moderskaps|understöd',
    'moderskapsförpackning': 'moderskaps|förpackning',
    'moderskapsförpackningen': 'moderskaps|förpackningen',
    'egendomsfördelning': 'egendoms|fördelning',
    'bodelningsmannen': 'bodelnings|mannen',
    'familjerådgivningen': 'familje|rådgivningen',
    'uppehållstillståndet': 'uppehålls|tillståndet',
    'underhållsförmågan': 'underhålls|förmågan',
    'underhållsförmåga': 'underhålls|förmåga',
    'underhållsbidraget': 'underhålls|bidraget',
    'underhållsskyldiga': 'underhålls|skyldiga',
    'uppfostringsmetod': 'uppfostrings|metod',
    'vänskapsförhållanden': 'vänskaps|förhållanden',
    'självbestämmanderätten': 'själv|bestämmande|rätten',
    'koncentrationssvårigheter': 'koncentrations|svårigheter',
    'föräldradagpenning': 'föräldra|dagpenning',
    'socialmyndigheter': 'social|myndigheter',
    'socialmyndigheters': 'social|myndigheters',
}
for word, pieces in COMPOUNDS.items():
    assert pieces.replace('|', '') == word


def draw_source_label(draw, label, xy, width, size, font_path, color, bottom=655):
    font = ImageFont.truetype(font_path, size)
    lines = []
    line = ''
    for word in label.split():
        if draw.textlength(word, font=font) > width:
            split = COMPOUNDS.get(word.casefold())
            if split:
                pieces = []
                offset = 0
                for part in split.split('|'):
                    pieces.append(word[offset:offset + len(part)])
                    offset += len(part)
                assert ''.join(pieces) == word
                pieces = [part + '-' for part in pieces[:-1]] + pieces[-1:]
            elif '-' in word:
                pieces = [part + '-' for part in word.split('-')[:-1]] + word.split('-')[-1:]
            else:
                if size > 22:
                    return draw_source_label(draw, label, xy, width, size - 1,
                                             font_path, color, bottom)
                raise ValueError('Explicit compound break needed: ' + word)
            if any(draw.textlength(part, font=font) > width for part in pieces):
                if size > 22:
                    return draw_source_label(draw, label, xy, width, size - 1,
                                             font_path, color, bottom)
                raise ValueError('Compound segment exceeds picture column: ' + word)
            if line:
                lines.append(line)
            lines.extend(pieces[:-1])
            line = pieces[-1]
            continue
        candidate = (line + ' ' + word).strip()
        if line and draw.textlength(candidate, font=font) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    if xy[1] + len(lines) * (size + 7) > bottom:
        if size > 22:
            return draw_source_label(draw, label, xy, width, size - 1,
                                     font_path, color, bottom)
        raise ValueError('Picture caption exceeds reserved height: ' + label)
    for index, line in enumerate(lines):
        assert draw.textlength(line, font=font) <= width
        draw.text((xy[0], xy[1] + index * (size + 7)), line, font=font,
                  fill=color, anchor='mt')
    return dict(lines=lines, font_size=size, width=width,
                bottom=xy[1] + len(lines) * (size + 7))
