
import dataclasses
import math
import taup
from .spherical import findTrianglePoints, distaz_deg, linInterpTDByDist
from .swat_result import SwatResult, Scatterer


class SWAT:
    def __init__(self, taupserver, evtdepth,
                 eq_scat_phase = "P,p,Ped",
                 sta_scat_revphase = "P,p,Ped",
                 model="prem"):
        self.taupserver = taupserver
        self.evtdepth = evtdepth
        self.eq_scat_phase = eq_scat_phase
        self.sta_scat_revphase = sta_scat_revphase
        self.model = model
        self.evtlat = 0
        self.evtlon =  0
        self.stalat = 0
        self.stalon = 0
        self.es_distdeg = 0
        self.es_az = 0
        self.es_baz = 0
        self.dist_step = 2
        self._mindepth=50
        self.backproject_depths = self.find_backproject_depths()
    def minDepth(self, val):
        self._mindepth=val
    def event(self, evtlat, evtlon):
        self.evtlat = evtlat
        self.evtlon =  evtlon
        self.es_distdeg, self.es_az, self.es_baz = distaz_deg(self.evtlat,
                                                           self.evtlon,
                                                           self.stalat,
                                                           self.stalon)
    def station(self, stalat, stalon):
        self.stalat = stalat
        self.stalon = stalon
        self.es_distdeg, self.es_az, self.es_baz = distaz_deg(self.evtlat,
                                                           self.evtlon,
                                                           self.stalat,
                                                           self.stalon)

    def find_backproject_depths(self):
        """
        Find depths in the model that might be endpoints for the back projecting
        rays. Should be the surface, 0, core mantle boundary and inner-outer
        core boundary as those are the boundaries where the phase name can
        change.
        """
        disconParams = taup.DisconQuery()
        disconParams.model(self.model)
        disconRes = disconParams.calc(self.taupserver)
        backproject_depths = [0]
        for discon in disconRes.models[0].discontinuities:
            if discon.preferredname in ["moho", "cmb", "iocb"]:
                backproject_depths.append(discon.depth)
        return backproject_depths

    def distaz(self):
        return distaz_deg(evtlat, evtlon, stalat, stalon)
    def scat_to_eq(self, scat_timedist, traveltimes, sta_scat_arrival, bazoffset=0, bazdelta=180):
        params = taup.TimeQuery()
        params.model(self.model)
        params.receiverdepth(scat_timedist.depth) # scatterer depth
        params.sourcedepth(self.evtdepth)
        params.seconds([t-scat_timedist.time for t in traveltimes])
        params.phase(self.eq_scat_phase)
        result = params.calc(self.taupserver)
        minbaz = self.es_baz-bazoffset-bazdelta
        scatterers = []
        for a in result.arrivals:
            if a.distdeg + scat_timedist.distdeg > self.es_distdeg:
                triangleAns  = findTrianglePoints(self.evtlat, self.evtlon, self.stalat, self.stalon, scat_timedist.distdeg, a.distdeg)
                if triangleAns is None:
                    continue
                pta, ptb, baz_offset, es_baz  = triangleAns
                pta_baz = pta[2]
                ptb_baz = ptb[2]
                tda = dataclasses.replace(scat_timedist, lat=pta[0], lon=pta[1])
                tdb = dataclasses.replace(scat_timedist, lat=ptb[0], lon=ptb[1])
                if bazdelta >= 180 or (pta_baz-minbaz) % 360 <= 2*bazdelta:
                    scatterers.append(Scatterer(
                        scat = tda,
                        scat_baz = pta_baz,
                        sta_scat_phase=sta_scat_arrival.phase,
                        sta_scat_rayparam=sta_scat_arrival.rayparam,
                        evt_scat = a))
                if bazdelta >= 180 or (ptb_baz-minbaz) % 360 <= 2*bazdelta:
                    scatterers.append(Scatterer(
                        scat = tdb,
                        scat_baz = ptb_baz,
                        sta_scat_phase=sta_scat_arrival.phase,
                        sta_scat_rayparam=sta_scat_arrival.rayparam,
                        evt_scat = a))
        return scatterers

    def check_path_points(self, sta_scat_arrival, traveltimes, bazoffset=0, bazdelta=180):
        """
        Check each path point from the given arrival, to see if it is a
        potential scattering point. The arrival should have been generated with
        path points, via a taup path query, and should be oriented as an
        inverse ray starting at the stations. Generally this is from a known
        ray parameter, and goes to the major discontinuity above or below. For
        example, when looking for a P wave scatterer in the mantle, the arrival
        would be generated as either a P ray from the station turning back
        to the surface, or as a Ped ray from the station that hits the core
        mantle boundary, as the given ray parameter may be too small to turn
        in the mantle.

        If an observed back azimuth and deltabaz are given, potential
        scatterers outside of this azimuthal range are eliminated.

        Returns a list of potential scatterers.
        """
        scat = []
        prevTD = None
        for seg in sta_scat_arrival.pathSegments:
            for td in seg.segment:
                if td.distdeg == 0 or td.depth < self._mindepth:
                    prevTD = td
                    continue
                if prevTD is not None and math.fabs(td.distdeg-prevTD.distdeg) > self.dist_step:
                    # need to interpolate between path points
                    num = math.ceil(math.fabs(td.distdeg-prevTD.distdeg)/self.dist_step)
                    step = (td.distdeg-prevTD.distdeg)/num
                    for n in range(num):
                        interpTD = linInterpTDByDist(prevTD, td, prevTD.distdeg+n*step)
                        scat = scat + self.scat_to_eq(interpTD,
                                                   traveltimes,
                                                   sta_scat_arrival,
                                                   bazoffset=bazoffset,
                                                   bazdelta=bazdelta)
                scat = scat + self.scat_to_eq(td,
                                       traveltimes,
                                       sta_scat_arrival,
                                       bazoffset=bazoffset,
                                       bazdelta=bazdelta)
                prevTD = td

        return scat

    def find_via_path(self, rayparamdegs, traveltimes, bazoffset=0, deltatime=0, bazdelta=180):
        if isinstance(rayparamdegs, float):
            rayparamdegs = [rayparamdegs]
        if isinstance(traveltimes, float):
            traveltimes = [traveltimes]
        params = taup.PathQuery()
        params.model(self.model)
        params.rayparamdeg(rayparamdegs)
        params.phase(self.sta_scat_revphase)
        params.receiverdepth(self.backproject_depths)
        # actually station, shoot ray back to scatterer
        # adding station as the "event" gives lat,lon for path points
        params.sourcedepth([0])
        if self.stalat is not None:
            params.event(self.stalat, self.stalon)
        result = params.calc(self.taupserver)
        scatterers = []
        for a in result.arrivals:
            spp = self.check_path_points(a, traveltimes, bazoffset=bazoffset, bazdelta=bazdelta)
            scatterers = scatterers + spp
        out = SwatResult(
            esdistdeg = self.es_distdeg,
            esaz = self.es_az,
            esbaz = self.es_baz,
            bazoffset = bazoffset,
            bazdelta = bazdelta,
            eq_scat_phase = self.eq_scat_phase,
            sta_scat_revphase = self.sta_scat_revphase,
            model = self.model,
            evtlat = self.evtlat,
            evtlon =  self.evtlon,
            evtdepth = self.evtdepth,
            stalat = self.stalat,
            stalon = self.stalon,
            rayparamdegs = rayparamdegs,
            traveltimes = traveltimes,
            mindepth = self._mindepth,
            scatterers = scatterers
        )
        return out
