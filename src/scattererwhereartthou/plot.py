

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

def mapplot(swatList, tauptimes=None, outfilename="swat_map.png", show=True):
    #plot on 2D map
    print('starting to plot 2D')
    if len(swatList) == 0:
        print("noting to plot...")
        return
    firstData = swatList[0]
    plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_feature(cfeature.OCEAN, color='lightskyblue',alpha=.2)
    ax.add_feature(cfeature.LAND, color="oldlace")
    gridlines=ax.gridlines(draw_labels=True, alpha=.80)
    plt.title(f'Scatter: rayp:{firstData.rayparamdegs} phase:{firstData.evt_scat_phase} - rev {firstData.sta_scat_revphase}  {makeBazTitle(firstData)}')

    if tauptimes is not None:
        for a in tauptimes.arrivals:
            alat = []
            alon = []
            for seg in a.pathSegments:
                for td in seg.segment:
                    alat.append(td.lat)
                    alon.append(td.lon)
            ax.plot(alon, alat, color='black')


    for swatData in swatList:
        ax.scatter(swatData.stalon, swatData.stalat, marker='v', s=20, color='blue')
        ax.scatter(swatData.evtlon, swatData.evtlat, marker='*', s=20, color='blue')
        for s in swatData.scatterers:
            ax.scatter(s.scat.lon, s.scat.lat, marker='.', color='tomato',alpha=.5)
    plt.savefig(outfilename, dpi=700, bbox_inches='tight', pad_inches=0.1)
    if show:
        print("Show map")
        plt.show()
    else:
        return None



def sliceplot(swatList, tauptimes=None, outfilename="swat_slice.png", show=True, rofe=6371):
    #plot on 2D map
    print('starting to plot 2D')
    if len(swatList) == 0:
        print("noting to plot...")
        return
    firstData = swatList[0]
    plt.figure()
    ax = plt.axes(projection='polar')

    plt.title(f'Scatter: rayp:{firstData.rayparamdegs} phase:{firstData.evt_scat_phase} - rev {firstData.sta_scat_revphase} {makeBazTitle(firstData)}')

    plt.scatter(0, 0, marker='v', s=20, color='blue')


    deepest = firstData.evtdepth
    if tauptimes is not None:
        for a in tauptimes.arrivals:
            adist = []
            adepth = []
            for seg in a.pathSegments:
                for td in seg.segment:
                    adist.append(math.radians(a.distdeg-td.distdeg))
                    adepth.append(rofe-td.depth)
                    if td.depth > deepest:
                        deepest = td.depth
            ax.plot(adist, adepth, color='black')


    maxESDeg = firstData.esdistdeg
    for swatData in swatList:
        if swatData.evtdepth > deepest:
            deepest = swatData.evtdepth
        if swatData.esdistdeg > maxESDeg:
            maxESDeg = swatData.esdistdeg
        plt.scatter(math.radians(swatData.esdistdeg), rofe-swatData.evtdepth, marker='*', s=20, color='blue')
        for s in swatData.scatterers:
            plt.scatter(math.radians(s.scat.distdeg), rofe-s.scat.depth, marker='.', color='tomato',alpha=.5)

    for swatData in swatList:
        for s in firstData.scatterers:
            if s.scat.depth > deepest:
                deepest = s.scat.depth
    deepest  *= 1.10 # little bit more
    maxESDeg *= 1.05
    print(f"ax.set_rmax({rofe})")
    print(f"ax.set_rmin({rofe}-{deepest})")
    print(f"ax.set_thetamax({maxESDeg})")

    ax.set_rmax(rofe)
    ax.set_rmin(rofe-deepest)
    ax.set_rorigin(0)
    ax.set_thetamin(0)
    ax.set_thetamax(maxESDeg)
    gridlines=ax.grid(True, alpha=.80)
    plt.savefig(outfilename, dpi=700, bbox_inches='tight', pad_inches=0.1)
    if show:
        print("Show slice")
        plt.show()
    else:
        return None

def makeBazTitle(swatData):
    bazTitle = ""
    if swatData.bazdelta < 180:
        bazTitle = f"Baz: {swatData.bazoffset}+-{swatData.bazdelta}"
    return bazTitle
