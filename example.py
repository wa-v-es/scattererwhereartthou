#!/usr/bin/env python

import taup
from scattererwhereartthou import SWAT, mapplot, sliceplot

#
# roughly equivalent to
# swat --evt 66 166 --eventdepth 0 --sta -11 120 --delay 0.1 --slow 5.087 --showmap --showslice

taup_path="../../../seis/TauP/build/install/TauP/bin/taup"
model="prem"
evt=(66, 166)
eventdepth=0
sta=(-11, 120)
phase="P"
slow=5.087
delay=0.1


with taup.TauPServer( taup_path=taup_path) as taupserver:
    params = taup.TimeQuery()
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
        ans = swat.find_via_path(slow,
                                 a.time+delay)
        swatList.append(ans)
    mapplot(swatList, tauptimes=timeResult)
    sliceplot(swatList, tauptimes=timeResult)
