#!/usr/bin/env python

import taup
from scattererwhereartthou import SWAT, mapplot, sliceplot
import matplotlib.pyplot as plt
plt.ion()
# location of taup version 3 executable, not needed if already on PATH
taup_path="../../TauP-3.2.0-SNAPSHOT6/bin/taup"

# -4.33 143.16 70.00 230402_180411_PA_inc2_r2.5
model="prem"    # velocity model
evt=(66, 166)   # eq lat, lon
eventdepth=200  # eq depth
sta=(-11, 120)  # station lat, lon
phase="P"   # reference phase
max_dist_step=.50 # max separation between path scatterers in degrees, default is 2 deg

# observed slownesses at station, usually p_minus, p, p_plus
# but can be more values for denser search results
# Note that the scatterer locations are quite sensitive to slowness, and so
# a denser gridsearch over slowness may be needed if the min-max range is large
slownesses=[5.5, 5.75, 6.0, 6.25]
# slownesses = [5.75+.05*p for p in range(-5, 6)]
# delay times relative to reference phase arrival, usually t_minus, t, t_plus
# but can be more values for denser search results
delaytimes=[5, 7.5, 10]
bazoffset=0
bazdelta=5


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
