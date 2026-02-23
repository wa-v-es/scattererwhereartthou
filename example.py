#!/usr/bin/env python

import taup
from scattererwhereartthou import SWAT, mapplot, sliceplot

#
# roughly equivalent to
# swat --evt 66 166 --eventdepth 0 --sta -11 120 --delay 15.0 --slow 4.0 --showmap --showslice

taup_path="../../../seis/TauP/build/install/TauP/bin/taup"
model="prem"
evt=(66, 166)
eventdepth=200
sta=(-11, 120)
phase="P"
slow=6.0
delay=20.0
max_dist_step=1.0 # max separation between path scatterers in degrees, default is 2 deg

with taup.TauPServer( taup_path=taup_path) as taupserver:
    params = taup.PathQuery() # so we can plot path
    params.model(model)
    params.event(*evt)
    params.sourcedepth(eventdepth)
    params.station(*sta)
    params.phase(phase)
    timeResult = params.calc(taupserver)
    swatList = []
    for a in timeResult.arrivals:
        print(f"Arrival: {a}")
        swat = SWAT(taupserver, eventdepth, model=model)
        swat.event(*evt)
        swat.station(*sta)
        swat.dist_step = max_dist_step # max dist deg between path point in degrees
        ans = swat.find_via_path(slow,
                                 a.time+delay)
        swatList.append(ans)
    mapplot(swatList, tauptimes=timeResult)
    sliceplot(swatList, tauptimes=timeResult)
