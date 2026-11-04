"""Minimal candidate compositor, for coordinator review; not used by production."""
from PIL import Image

def prepare_card(card):
    """Cache once when the active card/display segment changes."""
    return card.convert('RGB'), card.getchannel('A')

def compose_rgb(backdrop, progress, style, prepared_card, background_extent):
    """Preserve the existing floating crop extent and chosen Pillow resampler."""
    samplers = {'bicubic': Image.Resampling.BICUBIC, 'bilinear': Image.Resampling.BILINEAR}
    current = backdrop.resize((1920, 1080), resample=samplers[style.get('resampling', 'bicubic')],
                              box=background_extent(backdrop.size, progress, style))
    current.paste(prepared_card[0], (0, 0), prepared_card[1])
    return current
