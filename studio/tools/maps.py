"""Build episode maps from the pinned Natural Earth 5.1.2 country geometry."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'studio/media/sources/countries.geojson'
OUT = ROOT / 'studio/media/hb-c01-lage/maps'
NAMES = {'Finland': ('Finland', 26, 65), 'Sweden': ('Sverige', 16, 63), 'Norway': ('Norge', 9, 63), 'Denmark': ('Danmark', 9, 55.5), 'Iceland': ('Island', -19, 65), 'Russia': ('Ryssland', 34, 64), 'Estonia': ('Estland', 25.5, 58.4)}


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    features = json.loads(DATA.read_text())['features']
    project = Transformer.from_crs('EPSG:4326', '+proj=laea +lat_0=64 +lon_0=20 +datum=WGS84', always_xy=True).transform
    variants = [('finland_outline', ['Finland'], [], (18, 59, 33, 71))]
    variants += [('nordic_map', list(NAMES)[:5], ['Sweden', 'Norway', 'Denmark', 'Iceland'], (-27, 53, 38, 72))]
    for highlight in ['all', 'Russia', 'Norway', 'Sweden', 'Estonia']:
        variants.append(('neighbors_' + highlight.lower(), [k for k in NAMES if k not in ['Iceland', 'Denmark']], [highlight] if highlight != 'all' else ['Russia', 'Norway', 'Sweden', 'Estonia'], (6, 56, 39, 72)))
    for stem, labels, emphasized, bounds in variants:
        fig, ax = plt.subplots(figsize=(12, 9), dpi=160)
        fig.patch.set_facecolor('#dfebeb')
        ax.set_facecolor('#dfebeb')
        for feature in features:
            name = feature['properties']['ADMIN']
            geometry = feature['geometry']
            polygons = geometry['coordinates'] if geometry['type'] == 'MultiPolygon' else [geometry['coordinates']]
            color = '#e7bc70' if name == 'Finland' else '#96b9a9' if name in emphasized else '#c7d2cc'
            for polygon in polygons:
                for i, ring in enumerate(polygon):
                    x, y = project(*zip(*ring))
                    ax.add_patch(Polygon(list(zip(x, y)), facecolor=color if i == 0 else '#dfebeb', edgecolor='#6d837b', linewidth=.6, zorder=1))
        left, bottom, right, top = bounds
        corners = [project(x, y) for x in [left, right] for y in [bottom, top]]
        ax.set_xlim(min(p[0] for p in corners), max(p[0] for p in corners))
        ax.set_ylim(min(p[1] for p in corners), max(p[1] for p in corners))
        for name in labels:
            label, lon, lat = NAMES[name]
            ax.text(*project(lon, lat), label, ha='center', va='center', fontsize=17, color='#163f38', weight='bold', zorder=3, bbox=dict(facecolor='#f4f5ed', alpha=.9, edgecolor='none', boxstyle='round,pad=.25'))
        if stem.startswith('neighbors'):
            ax.annotate('Finska viken', xy=project(26, 60), xytext=project(34, 58), fontsize=13, color='#28566c', ha='center', arrowprops=dict(arrowstyle='-', color='#28566c'), zorder=4)
        ax.set_aspect('equal')
        ax.axis('off')
        fig.subplots_adjust(left=.02, right=.98, bottom=.04, top=.98)
        for suffix in ['png', 'svg']:
            fig.savefig(OUT / (stem + '.' + suffix), facecolor=fig.get_facecolor())
        plt.close(fig)
        print(stem)


if __name__ == '__main__':
    build()
