"""Explicit background and physical-setting photo choices for nine migration episodes."""
from pathlib import Path
import json
import re
import shutil

from housing_sources import normalize

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'studio/production/remaining'
FOREGROUNDS={
 'tillstand':{'picture-026':'File:Helsinki University Library Interior B - Marit Henriksson.jpg'},
 'tillstandstyper':{},
 'asyl':{
  'picture-016':'File:Vantaan vastaanottokeskus.jpg',
  'picture-031':'File:Halikon terveysasema.JPG'},
 'kvotflyktingar':{'picture-013':'File:Helsinki City Hall - Marit Henriksson.jpg'},
 'tillfalligt-skydd':{'picture-010':'File:Siikajärven vastaanottokeskus.jpg'},
 'familjeband':{},
 'beslut':{'picture-011':'File:Korkein hallinto-oikeus - Marit Henriksson.jpg'},
 'utan-tillstand':{
  'picture-013':'File:Huhtasuon terveysasema 2020.jpg',
  'picture-014':'File:Iitin terveysasema.jpg'},
 'medborgarskap':{},
}


def main():
    pages={}
    for folder in [BASE,ROOT/'studio/production/hb-c12a']:
        for path in folder.glob('*.json'):
            try:data=json.loads(path.read_text())
            except (ValueError,UnicodeDecodeError):continue
            if isinstance(data,dict):
                for page in data.get('query',{}).get('pages',{}).values():
                    if page.get('imageinfo'):pages[page['title']]=page
    reservations=json.loads((BASE/'media-reservations.json').read_text())
    old=json.loads((BASE/'used-media.json').read_text())
    catalogue=json.loads(Path('/tmp/hb-c06-current-music-catalogue.json').read_text())
    for name,choices in FOREGROUNDS.items():
        section='hb-c12-'+name;episode=ROOT/'studio/episodes'/section
        if (episode/'media-sources.json').exists():
            raise ValueError('Resume existing curated choice explicitly: '+section)
        reservation=reservations[section];background=reservation['background_file']
        if any(v['kind']=='background' and normalize(v['source_url'])==normalize(background) for v in old):
            raise ValueError('Previously used background: '+background)
        for other,value in reservations.items():
            if other!=section and value.get('background_file') and normalize(value['background_file'])==normalize(background):
                raise ValueError('Reserved elsewhere: '+other)
        photo=pages[background]['imageinfo'][0]
        music=next(row for row in catalogue if row['isrc']==reservation['music_isrc'])
        foreground={key:pages[title] for key,title in choices.items()}
        for candidate in [pages[background],*foreground.values()]:
            licence=candidate['imageinfo'][0]['extmetadata'].get('LicenseShortName',{}).get('value','')
            if not re.search(r'CC0|CC BY|Public domain',licence):
                raise ValueError('Review licence: '+candidate['title']+' '+licence)
        evidence=dict(photo_title=background,photo=photo,music=music,
            context='Photographed administrative,civic,healthcare,reception or UNHCR setting is identified from its actual source metadata. Historical reception-building photographs do not assert current operation,operator,address or access. Backgrounds are decorative context,not evidence that a person qualifies or a legal rule is current. No photographed individual is assigned nationality,protection,benefit or immigration status.',
            foreground_photos=foreground)
        (episode/'media-sources.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
        for helper in ['download_sources.py','prepare_assets.py']:
            shutil.copyfile(ROOT/'studio/episodes/hb-c11-atervinning'/helper,episode/helper)
        print(section,background,music['title'],len(foreground),'foreground photographs')


if __name__=='__main__':main()
