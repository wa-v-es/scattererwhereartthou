
import dataclasses
import taup
from .spherical import calcBackAz

class SWAT:
    def __init__(self, taupserver, eventdepth, evtstadeg,
                 toscatphase="P", fromscatphase="P", model="prem"):
        self.taupserver = taupserver
        self.eventdepth = eventdepth
        self.evtstadeg = evtstadeg
        self.toscatphase = toscatphase
        self.fromscatphase = fromscatphase
        self.model = model
        self.evtlat = None
        self.evtlon =  None
        self.stalat = None
        self.stalon = None
        self._mindepth=50
    def minDepth(self, val):
        self._mindepth=val
    def event(self, evtlat, evtlon):
        self.evtlat = evtlat
        self.evtlon =  evtlon
    def station(self, stalat, stalon):
        self.stalat = stalat
        self.stalon = stalon
    def scat_to_eq(self, timedist, traveltime, sta_scat_arrival):
        params = taup.TimeQuery()
        params.model(self.model)
        params.sourcedepth(timedist.depth) # scatterer depth
        params.receiverdepth(self.eventdepth)
        params.seconds(traveltime-timedist.time)
        params.phase(self.toscatphase)
        result = params.calc(self.taupserver)
        scatterers = []
        for a in result.arrivals:
            if a.distdeg + timedist.distdeg > self.evtstadeg:
                calcBackAzAns  = calcBackAz(self.evtlat, self.evtlon, self.stalat, self.stalon, timedist.distdeg, a.distdeg)
                if calcBackAzAns is None:
                    continue
                pta, ptb, C, es_baz  = calcBackAzAns
                tda = dataclasses.replace(timedist, lat=pta[0], lon=pta[1])
                tdb = dataclasses.replace(timedist, lat=ptb[0], lon=ptb[1])
                scatterers.append({
                    "scata": tda,
                    "scata_az": pta[2],
                    "scatb": tdb,
                    "scatb_az": ptb[2],
                    "C": C,
                    "es_baz": es_baz,
                    "scat_evt": a,
                    "sta_scat": sta_scat_arrival})
        return scatterers

    def check_path_points(self, sta_scat_arrival, traveltime):
        scat = []
        for seg in sta_scat_arrival.pathSegments:
            for td in seg.segment:
                if td.distdeg == 0:
                    continue
                if td.depth < self._mindepth:
                    continue
                #print(f"path: deg: {td.distdeg} depth: {td.depth}  time: {td.time}")
                scat = scat + self.scat_to_eq(td, traveltime, sta_scat_arrival)

        print(sta_scat_arrival)
        return scat

    def find_via_path(self, rayparamdeg, traveltime):
        params = taup.PathQuery()
        params.model(self.model)
        params.rayparamdeg(rayparamdeg)
        params.phase(self.fromscatphase)
        params.receiverdepth([0, 2889])
        # actually station, shoot ray back to scatterer
        # adding station as the "event" gives lat,lon for path points
        params.sourcedepth([0])
        if self.stalat is not None:
            params.event(self.stalat, self.stalon)
        result = params.calc(self.taupserver)
        scatterers = []
        out = {
            "eventdepth": self.eventdepth,
            "evtstadeg": self.evtstadeg,
            "toscatphase": self.toscatphase,
            "fromscatphase": self.fromscatphase,
            "model": self.model,
            "evtlat": self.evtlat,
            "evtlon":  self.evtlon,
            "stalat": self.stalat,
            "stalon": self.stalon,
            "rayparamdeg": rayparamdeg,
            "traveltime": traveltime,
            "mindepth": self._mindepth,
            "scatterers": scatterers
        }
        for a in result.arrivals:
            spp = self.check_path_points(a, traveltime)
            scatterers = scatterers + spp
        out["scatterers"] = scatterers
        return out
