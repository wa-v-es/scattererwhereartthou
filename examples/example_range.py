#!/usr/bin/env python

import taup
from scattererwhereartthou import SWAT, mapplot, sliceplot

# location of taup version 3 executable, not needed if already on PATH
taup_path="../../../seis/TauP/build/install/TauP/bin/taup"


model="prem"    # velocity model
evt=(66, 166)   # eq lat, lon
eventdepth=200  # eq depth
sta=(-11, 120)  # station lat, lon
phase="P"   # reference phase
max_dist_step=1.0 # max separation between path scatterers in degrees, default is 2 deg

# observed slownesses at station, usually p_minus, p, p_plus
# but can be more values for denser search results
# Note that the scatterer locations are quite sensitive to slowness, and so
# a denser gridsearch over slowness may be needed if the min-max range is large
slownesses=[5.5, 5.625, 5.75, 5.875, 6.0]
slownesses = [5.75+.05*p for p in range(-5, 6)]
# delay times relative to reference phase arrival, usually t_minus, t, t_plus
# but can be more values for denser search results
delaytimes=[5, 5.25, 5.5]
bazoffset=3
bazdelta=0.5


with taup.TauPServer( taup_path=taup_path) as taupserver:
    print("starting...")
    params = taup.PathQuery()
    params.model(model)
    params.event(*evt)
    params.sourcedepth(eventdepth)
    params.station(*sta)
    params.phase(phase)
    timeResult = params.calc(taupserver)

    swatList = []
    swat = SWAT(taupserver, eventdepth, model=model)
    swat.event(*evt)
    swat.station(*sta)
    swat.dist_step = max_dist_step

    for a in timeResult.arrivals:
        print(f"Arrival: {a}")
        traveltimes = [a.time+delay for delay in delaytimes]
        print(f"slow: {slownesses}  delay: {delaytimes} traveltimes: {traveltimes}")
        ans = swat.find_via_path(slownesses, traveltimes, bazoffset=bazoffset, bazdelta=bazdelta)
        swatList.append(ans)
    mapplot(swatList, tauptimes=timeResult)
    sliceplot(swatList, tauptimes=timeResult)
