"""Explicitly selected source photographs and music for eight housing episodes."""
from pathlib import Path
import json
import re
import shutil
import urllib.parse

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'studio/production/remaining'
SELECTIONS={
 'boendeformer':{
  'picture-016':'File:Hintantie 85 Oulu 20190428.jpg',
  'picture-018':'File:Merihaka apartment high-rises.JPG'},
 'hyresavtal':{
  'picture-040':'File:WMBUS Water Meter for submetering.jpg',
  'picture-046':'File:Ruuhonsaaren-sauna.jpg'},
 'hyresgast':{
  'picture-024':'File:2018-05-22 Cat and Dog, Cromer.JPG',
  'picture-033':'File:Kran 5655.jpg'},
 'agarbostad':{
  'picture-003':'File:Köydenpunojankatu 8 inner yard view 20220106 151809.jpg',
  'picture-004':'File:Olofsborg Helsinki upper facade.jpg'},
 'boendeproblem':{
  'picture-014':'File:Laundry room in apartment building.png',
  'picture-016':'File:Bidet shower.jpg'},
 'bostadsbidrag':{
  'picture-006':'File:Sallinkatu 1.jpg',
  'picture-027':'File:Diakonissalaitos asuinrakennus Alppikatu ja Kolmas Linja 2026 03 08 -1.jpg',
  'picture-030':'File:Naapurintie 10.jpg'},
 'ekonomi':{
  'mortgage':'File:Standertskjöldin talo Helsinki.jpg',
  'car_loan':'File:Mercedes-Benz S203 Yyteri kallerna.jpg'},
 'skulder':{
  'court_often':'File:HKIoikeussali.jpg',
  'small_oneoff':'File:Reading-Glasses.jpg'},
}


def normalize(value):
    return urllib.parse.unquote(value).rsplit('/wiki/',1)[-1].replace('_',' ').casefold()


def main():
    pages={}
    for path in BASE.glob('*.json'):
        try:data=json.loads(path.read_text())
        except (ValueError,UnicodeDecodeError):continue
        if isinstance(data,dict):
            for page in data.get('query',{}).get('pages',{}).values():
                if page.get('imageinfo'):pages[page['title']]=page
    reservations=json.loads((BASE/'media-reservations.json').read_text())
    old=json.loads((BASE/'used-media.json').read_text())
    catalogue=json.loads(Path('/tmp/hb-c06-current-music-catalogue.json').read_text())
    for name,photos in SELECTIONS.items():
        section='hb-c11-'+name
        episode=ROOT/'studio/episodes'/section
        if (episode/'media-sources.json').exists():
            raise ValueError('Do not replace existing curated selection: '+section)
        reservation=reservations[section]
        background=reservation['background_file']
        if any(v['kind']=='background' and normalize(v['source_url'])==normalize(background) for v in old):
            raise ValueError('Already-used background: '+background)
        for other,value in reservations.items():
            if other!=section and value.get('background_file') and normalize(value['background_file'])==normalize(background):
                raise ValueError('Background reserved elsewhere: '+other)
        photo=pages[background]['imageinfo'][0]
        music=next(row for row in catalogue if row['isrc']==reservation['music_isrc'])
        foreground={key:pages[title] for key,title in photos.items()}
        for candidate in [pages[background],*foreground.values()]:
            meta=candidate['imageinfo'][0]['extmetadata']
            licence=meta.get('LicenseShortName',{}).get('value','')
            if not re.search(r'CC0|CC BY|Public domain',licence):
                raise ValueError('Review reuse licence: '+candidate['title']+' '+licence)
        evidence=dict(photo_title=background,photo=photo,music=music,
            context='Verified Finnish building exterior used as decorative setting only; no pictured person assigned tenancy,debt,benefit or ownership status. Foreground object photographs retain their actual documented locations; they do not demonstrate a current Finnish legal rule.',
            foreground_photos=foreground)
        (episode/'media-sources.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
        for helper in ['download_sources.py','prepare_assets.py']:
            shutil.copyfile(ROOT/'studio/episodes/hb-c11-atervinning'/helper,episode/helper)
        print(section,background,music['title'],len(foreground),'photos')


if __name__=='__main__':main()
