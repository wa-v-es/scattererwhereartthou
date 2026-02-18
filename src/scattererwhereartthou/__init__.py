
__version__="0.0.1"

from .swat import SWAT
from .plot import mapplot, sliceplot
from .swat_result import SwatResult, Scatterer

__all__ = [
    "SWAT",
    "SwatResult",
    "Scatterer",
    "spherical",
    "mapplot",
    "sliceplot"
]
