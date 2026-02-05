

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
    plt.title(f'Scatter:{firstData["traveltime"]} rayp:{firstData["rayparamdeg"]} phase:{firstData["toscatphase"]} - {firstData["fromscatphase"]}')

    plt.scatter(firstData["stalon"], firstData["stalat"], marker='v', s=20, color='blue')
    plt.scatter(firstData["evtlon"], firstData["evtlat"], marker='*', s=20, color='blue')

    for s in firstData["scatterers"]:
        plt.scatter(s["scata"].lon, s["scata"].lat, marker='.', color='tomato')
        plt.scatter(s["scatb"].lon, s["scatb"].lat, marker='.', color='tomato')
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
    plt.figure()
    ax = plt.axes(projection='polar')
    gridlines=ax.grid(True, alpha=.80)
    plt.title(f'Scatter:{firstData["traveltime"]} rayp:{firstData["rayparamdeg"]} phase:{firstData["toscatphase"]} - {firstData["fromscatphase"]}')

    plt.scatter(0, 0, marker='v', s=20, color='blue')
    plt.scatter(math.radians(firstData["evtstadeg"]), firstData["eventdepth"], marker='*', s=20, color='blue')

    for s in firstData["scatterers"]:
        plt.scatter(math.radians(s["scata"].distdeg), rofe-s["scata"].depth, marker='.', color='tomato')
        plt.scatter(math.radians(s["scatb"].distdeg), rofe-s["scatb"].depth, marker='.', color='tomato')
    plt.savefig(outfilename, dpi=700, bbox_inches='tight', pad_inches=0.1)
    if show:
        print("Show map")
        plt.show()
    else:
        return None
