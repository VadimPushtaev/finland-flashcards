"""Render source-named city pointers using pinned Natural Earth geometry."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[3]
MEDIA = ROOT / 'studio/media/hb-c01-regioner'
MAPS = {'south': ('Helsinki', 'Helsingfors'), 'lakes': ('Tampere', 'Tammerfors'),
        'west': ('Vaasa', 'Vasa'), 'north': ('Rovaniemi', 'Rovaniemi'),
        'islands': ('Mariehamn', 'Mariehamn')}

def build():
    countries = json.loads((ROOT / 'studio/media/sources/countries.geojson').read_text())['features']
    places = json.loads((MEDIA / 'sources/places.geojson').read_text())['features']
    project = Transformer.from_crs('EPSG:4326', '+proj=laea +lat_0=64 +lon_0=26 +datum=WGS84', always_xy=True).transform
    output = MEDIA / 'maps'
    output.mkdir(parents=True, exist_ok=True)
    for scene, (name, label) in MAPS.items():
        point = next(p for p in places if p['properties']['NAME'] == name and p['properties']['SOV0NAME'] == 'Finland')
        fig, ax = plt.subplots(figsize=(10, 9.5), dpi=140)
        fig.patch.set_facecolor('#dfebeb')
        ax.set_facecolor('#dfebeb')
        for feature in countries:
            if feature['properties']['ADMIN'] not in ['Finland','Sweden','Norway','Russia','Estonia']:
                continue
            polygons = feature['geometry']['coordinates']
            if feature['geometry']['type'] != 'MultiPolygon':
                polygons = [polygons]
            for polygon in polygons:
                for i, ring in enumerate(polygon):
                    x, y = project(*zip(*ring))
                    fill = ('#a2bfae' if feature['properties']['ADMIN'] == 'Finland' else '#cbd6d0') if i == 0 else '#dfebeb'
                    ax.add_patch(Polygon(list(zip(x,y)), facecolor=fill, edgecolor='#6d837b', linewidth=.7))
        x,y = project(*point['geometry']['coordinates'])
        ax.scatter([x],[y],s=100,c='#a46214',edgecolor='#fff8de',linewidth=2,zorder=4)
        offset = (30,0) if scene in ['west','islands'] else (-25,0)
        ax.annotate(label, (x,y), xytext=offset, textcoords='offset points', ha='left' if offset[0]>0 else 'right', va='center', fontsize=22, weight='bold', color='#163f38', zorder=5,
                    bbox=dict(facecolor='#f6f1e6',edgecolor='none',alpha=.94,boxstyle='round,pad=.25'),arrowprops=dict(arrowstyle='-',color='#a46214'))
        ax.text(*project(28.5,65), 'Finland', fontsize=21,color='#163f38',ha='center')
        corners=[project(lon,lat) for lon in [17,34] for lat in [59.1,70.6]]
        ax.set_xlim(min(p[0] for p in corners),max(p[0] for p in corners));ax.set_ylim(min(p[1] for p in corners),max(p[1] for p in corners))
        ax.set_aspect('equal');ax.axis('off');fig.subplots_adjust(left=.02,right=.98,bottom=.02,top=.98)
        for ext in ['png','svg']:
            fig.savefig(output/(scene+'.'+ext),facecolor=fig.get_facecolor())
        plt.close(fig)
        print(scene,label,point['geometry']['coordinates'])

if __name__ == '__main__':
    build()
