#!/usr/bin/env python

import taup
from scattererwhereartthou import SWAT, mapplot, sliceplot


taup_path="../../../seis/TauP/build/install/TauP/bin/taup"
model="prem"
evt=(66, 166)
eventdepth=0
sta=(-11, 120)
phase="P"
slowrange=(4.5,4.8,0.2)  # min, max, step
delayrange=(5,7,1.0)     # min, max, step
bazoffset=3
bazdelta=0.5


with taup.TauPServer( taup_path=taup_path) as taupserver:
    print("starting...")
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
        slow = slowrange[0]
        while slow <= slowrange[1]:
            delay = delayrange[0]
            while delay <= delayrange[1]:
                print(f"slow: {slow}  delay: {delay}")
                ans = swat.find_via_path(slow, a.time+delay, bazoffset=bazoffset, bazdelta=bazdelta)
                swatList.append(ans)
                delay += delayrange[2]
            slow += slowrange[2]
    mapplot(swatList, tauptimes=timeResult)
    sliceplot(swatList, tauptimes=timeResult)
