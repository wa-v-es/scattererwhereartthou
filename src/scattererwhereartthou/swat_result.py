from dataclasses import dataclass
from taup import TimeDist, Arrival

@dataclass
class Scatterer:
    """Class to hold a potential scatterer"""
    scat: TimeDist
    scat_baz: float
    sta_scat_phase: str
    sta_scat_rayparam: float
    evt_scat: Arrival

@dataclass
class SwatResult:
    """Class for SWAT results."""

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
    evtdepth: float
    stalat: float
    stalon: float
    rayparamdegs: list[float]
    traveltimes: list[float]
    mindepth: float
    scatterers: list[Scatterer]
