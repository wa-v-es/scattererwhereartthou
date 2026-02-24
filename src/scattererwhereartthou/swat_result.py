from dataclasses import dataclass
from taup import TimeDist, Arrival

@dataclass
class Scatterer:
    """Class to hold a potential scatterer"""
    scat: TimeDist
    scat_baz: float
    sta_scat_phase: str
    scat_evt: Arrival

@dataclass
class SwatResult:
    """Class for SWAT results."""

    eventdepth: float
    esdistdeg: float
    esaz: float
    esbaz: float
    bazoffset: float
    bazdelta: float
    eq_scat_phase: list[str]
    sta_scat_revphase: list[str]
    model: str
    evtlat: float
    evtlon:  float
    stalat: float
    stalon: float
    rayparamdeg: float
    traveltime: float
    mindepth: float
    scatterers: list[Scatterer]
