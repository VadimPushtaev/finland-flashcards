"""Rebuild source-only foreground text cards for this episode."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
CARDS={'outdoors': ('Friluftsliv', ['fiske', 'terrängcykling', 'vinterbadande', 'vandring'])}
FONTS=Path('/System/Library/Fonts/Supplemental')
for slug,(heading,lines) in CARDS.items():
    image=Image.new('RGB',(1000,950),'#102e2b');d=ImageDraw.Draw(image)
    d.rounded_rectangle((25,25,975,925),radius=30,outline='#e7bc70',width=3)
    face=ImageFont.truetype(str(FONTS/'Arial Bold.ttf'),52)
    while face.getlength(heading)>850:face=ImageFont.truetype(str(FONTS/'Arial Bold.ttf'),face.size-1)
    d.text((500,140),heading,font=face,fill='#e7bc70',anchor='mm')
    for n,line in enumerate(lines):
        face=ImageFont.truetype(str(FONTS/'Arial.ttf'),46)
        while face.getlength(line)>850:face=ImageFont.truetype(str(FONTS/'Arial.ttf'),face.size-1)
        d.text((500,310+n*105),line,font=face,fill='#f6f1e6',anchor='mm')
    output=ROOT/'studio/media'/Path(__file__).parent.name/'graphics';output.mkdir(parents=True,exist_ok=True)
    image.save(output/(slug+'.png'))
