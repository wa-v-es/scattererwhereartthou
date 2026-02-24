#!/usr/bin/env python

import taup
from scattererwhereartthou import SWAT, mapplot, sliceplot

#
# roughly equivalent to
# swat --evt 66 166 --eventdepth 200 --sta -11 120 --delay 20.0 --slow 6.0 --showmap --showslice

# location of taup version 3 executable, not needed if already on PATH
taup_path="../../../seis/TauP/build/install/TauP/bin/taup"

model="prem"    # velocity model
evt=(66, 166)   # eq lat, lon
eventdepth=200  # eq depth
sta=(-11, 120)  # station lat, lon
phase="P"   # reference phase
slow=6.0    # observed slowness from scatterer at station
delay=20.0  # time delay relative to reference phase arrival
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
        swat.dist_step = max_dist_step
        ans = swat.find_via_path(slow,
                                 a.time+delay)
        swatList.append(ans)
    mapplot(swatList, tauptimes=timeResult)
    sliceplot(swatList, tauptimes=timeResult)
