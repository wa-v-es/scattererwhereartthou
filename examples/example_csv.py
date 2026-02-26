#!/usr/bin/env python

"""
Simple example of saving output to a CSV file.
"""

import csv
import taup
from scattererwhereartthou import SWAT, mapplot, sliceplot

# location of taup version 3 executable, not needed if already on PATH
taup_path="../../TauP-3.2.0-SNAPSHOT6/bin/taup"

# -4.33 143.16 70.00 230402_180411_PA_inc2_r2.5
# la/lo/elv: 64.67 -155.88 362 TA (GSA) (grid 65, -157)

model="iasp91"    # velocity model
evt=(-4.33, 143.16)   # eq lat, lon
eventdepth=70  # eq depth
sta=(64.67, -155.88)  # station lat, lon
phase="P"   # reference phase
max_dist_step=1.0 # max separation between path scatterers in degrees, default is 2 deg


# observed slownesses at station, usually p_minus, p, p_plus
# but can be more values for denser search results
# Note that the scatterer locations are quite sensitive to slowness, and so
# a denser gridsearch over slowness may be needed if the min-max range is large
# slownesses = [5.75+.05*p for p in range(-5, 6)]
slownesses = [6+.1*p for p in range(2)]

# delay times relative to reference phase arrival, usually t_minus, t, t_plus
# but can be more values for denser search results
delaytimes = list(range(50, 171, 5))
delaytimes=[50,55]
bazoffset=0
bazdelta=5
sta_scat_revphase="p,P,Ped,pP,PP"
evt_scat_phase="p,P,Ped,pP,PP"


with open("swat_try.csv", "w", newline='') as outcsv:
    csvwriter = csv.writer(outcsv)
    csvwriter.writerow(["scatlat", "scatlon", "scatdepth",
                        "scatdistdeg", "scatbaz", "sta_scat_p", "scat_time",
                        'sta_scat_phase','evt_scat_phase'
                        "evtlat", "evtlon", "evtdepth",
                        "stalat", "stalon",'baz_GCP'
                        ])
    with taup.TauPServer( taup_path=taup_path) as taupserver:
        print("starting...")
        # reference phase
        params = taup.PathQuery()
        params.model(model)
        params.event(*evt)
        params.sourcedepth(eventdepth)
        params.station(*sta)
        params.phase(phase)
        timeResult = params.calc(taupserver)

        swatList = []
        swat = SWAT(taupserver, eventdepth, model=model,
            sta_scat_revphase=sta_scat_revphase,
            evt_scat_phase=evt_scat_phase)
        swat.event(*evt)
        swat.station(*sta)
        swat.dist_step = max_dist_step

        for a in timeResult.arrivals:
            print(f"Arrival: {a}")
            traveltimes = [a.time+delay for delay in delaytimes]
            print(f"slow: {slownesses}  delay: {delaytimes} traveltimes: {traveltimes}")
            ans = swat.find_via_path(slownesses, traveltimes, bazoffset=bazoffset, bazdelta=bazdelta)
            swatList.append(ans)
            for sc in ans.scatterers:
                csvwriter.writerow([format(sc.scat.lat, "0.3f"), format(sc.scat.lon, "0.3f"),
                                    format(sc.scat.depth, "0.3f"),
                                    format(sc.scat.distdeg, "0.2f"),
                                    format(sc.scat_baz, "0.3f"),
                                    format(sc.sta_scat_rayparam, "0.2f"),
                                    format(sc.scat.time+sc.evt_scat.time, "0.2f"),
                                    sc.sta_scat_phase,sc.evt_scat.phase,
                                    ans.evtlat, ans.evtlon, ans.evtdepth,
                                    ans.stalat, ans.stalon,format(ans.esbaz, "0.3f")
                                    ])
