import matplotlib.pyplot as plt
from matplotlib import cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import json
import math
import glob,re,sys

import matplotlib as mpl
import pyproj
import numpy as np
#####
def makeBazTitle(firstData):
    bazTitle = ""
    if firstData["bazdelta"] < 180:
        bazTitle = f"Baz: {firstData['bazoffset']}+-{firstData['bazdelta']}"
    return bazTitle

def extract_seconds(fname):
    # matches "..._11s.json" or "..._11s" anywhere in the filename
    m = re.search(r'(\d+)\s*s(?=\.json$)', fname)
    if not m:
        # fallback: find last number before 's' anywhere
        m = re.search(r'(\d+)s', fname)
    if not m:
        raise ValueError(f"Can't parse seconds from filename: {fname}")
    return int(m.group(1))

folder_pattern = "slow_5_time/*.json"
files = sorted(glob.glob(folder_pattern))

cmap = plt.get_cmap("plasma")   # pick any: viridis, plasma, turbo, etc.
norm = mpl.colors.Normalize(vmin=0, vmax=.1)  # 1–20 sec
# norm = mpl.colors.Normalize(vmin=1, vmax=20)  # 1–20 sec

geod=pyproj.Geod(ellps="WGS84")

fig, ax=plt.subplots()

plt.axis('off')

ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_feature(cfeature.OCEAN, color='grey',alpha=.2)
ax.add_feature(cfeature.LAND, color="oldlace")
gridlines=ax.gridlines(draw_labels=True, alpha=.50)
for fn in files:
    tsec = extract_seconds(fn)
    color = cmap(norm(tsec))

    with open(fn, "r") as j:
        mydata = json.load(j)

        # print(data)
        print('starting to plot 2D')
        if len(mydata["swat"]) == 0:
            print("noting to plot...")
            continue
        firstData = mydata["swat"][0]
        # plt.figure()
        plt.title(f'Scatter: rayp:{firstData["rayparamdeg"]} phase:{firstData["toscatphase"]} - {firstData["fromscatphase"]}  {makeBazTitle(firstData)}')

        for s in firstData["scatterers"]:
            plt.scatter(s["scat"]['lon'], s["scat"]['lat'], edgecolors='black', s=40,lw=.2, marker='.', color=color,alpha=.6)

plt.scatter(firstData["stalon"], firstData["stalat"], marker='v', s=60, color='navy')
plt.scatter(firstData["evtlon"], firstData["evtlat"], marker='*', s=60, color='navy')

line_arc=geod.inv_intermediate(firstData["stalon"],firstData["stalat"],firstData["evtlon"], firstData["evtlat"],npts=300)
lon_points=np.array(line_arc.lons)
lat_points=np.array(line_arc.lats)
plt.plot(lon_points, lat_points, transform=ccrs.Geodetic(),color='darkgreen',lw=.65,alpha=.6)


sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax,shrink=.6,pad=.1)
cbar.set_label("Delay time (s)")
# plt.show()
plt.savefig('slow_5_P5.png', dpi=300, bbox_inches='tight', pad_inches=0.1)
