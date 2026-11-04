"""Original neutral medical-object glyphs for advisory plans, under repo MIT.

These are isolated objects, without brands, doses, patients or use instructions.
C10 may call the function from its owned renderer with the chapter palette.
"""


def draw_medical_object(draw, kind, cx, cy, scale=1, stroke='#e6c384', fill=None):
    def point(x, y):
        return cx + x * scale, cy + y * scale

    def line(points, width=5):
        draw.line([point(*value) for value in points], fill=stroke,
                  width=max(2, round(width * scale)), joint='curve')

    def rectangle(x1, y1, x2, y2, radius=8):
        draw.rounded_rectangle((*point(x1, y1), *point(x2, y2)),
                               radius=radius * scale, outline=stroke,
                               width=max(2, round(5 * scale)), fill=fill)

    if kind == 'syringe':
        rectangle(-25, -51, 25, 54, radius=4)
        line([(-42, 54), (42, 54)])
        line([(0, 56), (0, 86)])
        line([(-33, 87), (33, 87)], width=8)
        line([(-14, -52), (-10, -75), (10, -75), (14, -52)])
        line([(0, -75), (0, -118)], width=3)
    elif kind == 'condom_pack':
        rectangle(-82, -76, 82, 76, radius=10)
        draw.ellipse((*point(-44, -44), *point(44, 44)), outline=stroke,
                     width=max(2, round(6 * scale)))
        draw.ellipse((*point(-30, -30), *point(30, 30)), outline=stroke,
                     width=max(2, round(3 * scale)))
        for x in range(-61, 70, 22):
            line([(x, -75), (x, -65)], width=2)
            line([(x, 65), (x, 75)], width=2)
    elif kind == 'barrier_sheet':
        line([(-86, -70), (53, -70), (86, -38), (86, 70),
              (-86, 70), (-86, -70)])
        line([(53, -70), (53, -38), (86, -38)], width=3)
        line([(-73, 58), (73, 58)], width=2)
    else:
        raise ValueError('Unknown original medical object: ' + kind)
