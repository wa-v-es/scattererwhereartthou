import math
from taup import TimeDist

DtoR=math.pi/180.0
RtoD=1/DtoR

def findTrianglePoints(evtlat, evtlon, stalat, stalon, staToScatDist, evtToScatDist):
    """
    calculates 2 points that satisfy triangle
    returns (lat, lon, baz), (lat, lon, baz), C
    """
    esdistR, esAzR, esBazR = distaz_radian(evtlat, evtlon, stalat, stalon)
    staToScatDistR = math.radians(staToScatDist)
    evtToScatDistR = math.radians(evtToScatDist)
    if (esdistR > staToScatDistR + evtToScatDistR
        or staToScatDistR > esdistR + evtToScatDistR
        or evtToScatDistR > esdistR + staToScatDistR):
        # can't make a triangle as event station too far
        return None

    C = math.acos((math.cos(evtToScatDistR)-math.cos(staToScatDistR)*math.cos(esdistR))
                            / (math.sin(staToScatDistR)*math.sin(esdistR)))

    CPlus = (esBazR+C)*RtoD
    CMinus = (esBazR-C)*RtoD
    llPlus = latLonFor(stalat, stalon, staToScatDist, CPlus)
    llMinus = latLonFor(stalat, stalon, staToScatDist, CMinus)
    return (( llPlus[0], llPlus[1], CPlus), ( llMinus[0], llMinus[1], CMinus), C*RtoD, esBazR*RtoD)


def distaz_deg(evtlat, evtlon, stalat, stalon):
    distR, azR, bazR = distaz_radian(evtlat, evtlon, stalat, stalon)
    return distR*RtoD, azR*RtoD, bazR*RtoD

def distaz_radian(evtlat, evtlon, stalat, stalon):
    elatR = math.radians(evtlat)
    elonR = math.radians(evtlon)
    slatR = math.radians(stalat)
    slonR = math.radians(stalon)
    distR = math.acos(math.sin(slatR)*math.sin(elatR)
                     +math.cos(slatR)*math.cos(elatR)*math.cos(slonR-elonR))
    azR =azimuthR(elatR, elonR, slatR, slonR, distR)
    bazR =azimuthR(slatR, slonR, elatR, elonR, distR)
    return distR, azR, bazR

def latLonFor(startlat, startlon, dist, azimuth):
    slatr = math.radians(startlat)
    slonr = math.radians(startlon)
    distr = math.radians(dist)
    azr = math.radians(azimuth)
    latr = math.asin(math.cos(azr)*math.sin(distr)*math.cos(slatr)
                           +math.cos(distr)*math.sin(slatr))
    sinlon = math.sin(azr)*math.sin(distr)/math.cos(latr)
    coslon = ((math.cos(distr)-math.sin(slatr)*math.sin(latr))
            / (math.cos(slatr)*math.cos(latr)))
    lon = startlon + RtoD*math.atan2(sinlon, coslon)
    lon = ensureLonInRange(lon)
    return latr*RtoD, lon

def azimuthR(latAR, lonAR, latBR, lonBR, distR=None):
    if distR is None:
        distR=distance(latAR, lonAR, latBR, lonBR)
    cosAzimuth = ((math.cos(latAR) * math.sin(latBR) - math.sin(latAR)
                * math.cos(latBR) * math.cos((lonBR - lonAR)))
                / math.sin(distR))
    sinAzimuth = (math.cos(latBR)
                * math.sin((lonBR - lonAR))
                / math.sin(distR))
    return math.atan2(sinAzimuth, cosAzimuth);

def ensureLonInRange(lon):
    return ensureDegInRange(lon)

def ensureDegInRange(val):
    if val <= -180:
        val+=360
    if val > 180:
        val -= 360
    return val

def hav(theta):
    return (1-math.cos(theta))/2

def invhav(h):
    return 2*math.asin(math.sqrt(h))

def linInterpTDByDist(a, b, distdeg):
    time = linearInterp(a.distdeg, a.time, b.distdeg, b.time, distdeg)
    depth = linearInterp(a.distdeg, a.depth, b.distdeg, b.depth, distdeg)
    lat = None
    if a.lat is not None and b.lat is not None:
        lat = linearInterp(a.distdeg, a.lat, b.distdeg, b.lat, distdeg)
    lon = None
    if a.lon is not None and b.lon is not None:
        lat = linearInterp(a.distdeg, a.lon, b.distdeg, b.lon, distdeg)
    return TimeDist(distdeg, depth, time, lat, lon)

def linearInterp(xa, ya, xb, yb, x):
    if x == xa:
        return ya
    if x == xb:
        return yb
    return (yb - ya) * (x - xa) / (xb - xa) + ya
