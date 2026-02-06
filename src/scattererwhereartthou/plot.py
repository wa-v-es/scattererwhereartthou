

import matplotlib.pyplot as plt
from matplotlib import cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import json
import math
import sys


import matplotlib.pyplot as plt
from matplotlib import cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import json
import sys

def mapplot(mydata, outfilename="swat_map.png", show=True):
    #plot on 2D map
    print('starting to plot 2D')
    if len(mydata["swat"]) == 0:
        print("noting to plot...")
        return
    firstData = mydata["swat"][0]
    plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_feature(cfeature.OCEAN, color='lightskyblue')
    ax.add_feature(cfeature.LAND, color="oldlace")
    gridlines=ax.gridlines(draw_labels=True, alpha=.80)
    plt.title(f'Scatter: rayp:{firstData["rayparamdeg"]} phase:{firstData["toscatphase"]} - {firstData["fromscatphase"]}  {makeBazTitle(firstData)}')

    plt.scatter(firstData["stalon"], firstData["stalat"], marker='v', s=20, color='blue')
    plt.scatter(firstData["evtlon"], firstData["evtlat"], marker='*', s=20, color='blue')

    for s in firstData["scatterers"]:
        plt.scatter(s["scat"].lon, s["scat"].lat, marker='.', color='tomato')
    plt.savefig(outfilename, dpi=700, bbox_inches='tight', pad_inches=0.1)
    if show:
        print("Show map")
        plt.show()
    else:
        return None



def sliceplot(mydata, outfilename="swat_slice.png", show=True, rofe=6371):
    #plot on 2D map
    print('starting to plot 2D')
    if len(mydata["swat"]) == 0:
        print("noting to plot...")
        return
    firstData = mydata["swat"][0]
    deepest = 0
    for s in firstData["scatterers"]:
        if s["scat"].depth > deepest:
            deepest = s["scat"].depth
    for a in firstData["backrays"].arrivals:
        for s in a.pathSegments:
            for ss in s.segment:
                if ss.depth > deepest:
                    deepest = ss.depth
    deepest = deepest * 1.10 # little bit more
    plt.figure()
    ax = plt.axes(projection='polar')
    print(f"ax.set_rmax({rofe})")
    print(f"ax.set_rmin({rofe}-{deepest})")

    plt.title(f'Scatter: rayp:{firstData["rayparamdeg"]} phase:{firstData["toscatphase"]} - {firstData["fromscatphase"]} {makeBazTitle(firstData)}')

    plt.scatter(math.radians(firstData["esdistdeg"]), firstData["eventdepth"], marker='*', s=20, color='blue')

    for s in firstData["scatterers"]:
        plt.scatter(math.radians(s["scat"].distdeg), rofe-s["scat"].depth, marker='.', color='tomato')


    ax.set_rmax(rofe)
    ax.set_rmin(rofe-deepest)
    ax.set_rorigin(0)
    ax.set_thetamin(0)
    ax.set_thetamax(firstData["esdistdeg"]*1.05)
    gridlines=ax.grid(True, alpha=.80)
    plt.savefig(outfilename, dpi=700, bbox_inches='tight', pad_inches=0.1)
    if show:
        print("Show slice")
        plt.show()
    else:
        return None

def makeBazTitle(firstData):
    bazTitle = ""
    if firstData["bazdelta"] < 180:
        bazTitle = f"Baz: {firstData['bazoffset']}+-{firstData['bazdelta']}"
    return bazTitle
