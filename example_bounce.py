#!/usr/bin/env python

import taup
from scattererwhereartthou import SWAT, mapplot, sliceplot

#
# roughly equivalent to
# swat --evt 66 166 --eventdepth 0 --sta -11 120 --delay 15.0 --slow 4.0 --showmap --showslice

# location of taup version 3 executable, not needed if already on PATH
taup_path="../../../seis/TauP/build/install/TauP/bin/taup"

model="prem"    # velocity model
evt=(66, 166)   # eq lat, lon
eventdepth=200  # eq depth
sta=(-11, 120)  # station lat, lon
phase="P"   # reference phase
slow=6.0    # observed slowness from scatterer at station
delay=200.0  # time delay relative to reference phase arrival
max_dist_step=1.0 # max separation between path scatterers in degrees, default is 2 deg

# adding pP and PP allows a surface bounce between station and scatterer
# default is p,P,Ped to cover normal incident P wave at station in reverse direction
# sense of phase is reversed, station to scatterer and on past, at given ray param
sta_scat_revphase="p,P,Ped,pP,PP"
# adding pP and PP allows a surface bounce between earthquake and scatterer
# default is p,P,Ped to cover normal P wave to scatterer
# sense of phase is earthquake to scatterer
evt_scat_phase="p,P,Ped,pP,PP"

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
        swat = SWAT(taupserver, eventdepth, model=model,
                    sta_scat_revphase=sta_scat_revphase,
                    evt_scat_phase=evt_scat_phase)
        swat.event(*evt)
        swat.station(*sta)
        swat.dist_step = max_dist_step
        ans = swat.find_via_path(slow,
                                 a.time+delay)
        swatList.append(ans)
    mapplot(swatList, tauptimes=timeResult)
    sliceplot(swatList, tauptimes=timeResult)
