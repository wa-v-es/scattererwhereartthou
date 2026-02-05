
from .swat import SWAT
from .plot import mapplot, sliceplot
from . import __version__

import argparse
import json
import pathlib
import sys
import taup

def runswat(args):
    with taup.TauPServer( taup_path=args.taup) as taupserver:
        params = taup.TimeQuery()
        params.model(args.model)
        evtlat = args.evt[0]
        evtlon = args.evt[1]
        params.event(evtlat, evtlon)
        params.sourcedepth(args.eventdepth)
        stalat = args.sta[0]
        stalon = args.sta[1]
        params.station(stalat, stalon)
        params.phase(args.phase)
        result = params.calc(taupserver)
        swatList = []
        output = {
            "taup": result,
            "swat": swatList
        }

        toscatphase = "P,p,Ped"
        fromscatphase = "P,p,Ped"

        if len(result.arrivals) == 0:
            print(f"No arrivals for {ref_phase} for {evtlat},{evtlon} ({eventdepth} km) to {stalat},{stalon}")
        else:
            for a in result.arrivals[:1]:
                if args.verbose:
                    print(f"Arrival: {a}")
                swat = SWAT(taupserver, args.eventdepth, a.distdeg, toscatphase, fromscatphase, model=args.model)
                swat.event(evtlat, evtlon)
                swat.station(stalat, stalon)
                ans = swat.find_via_path(args.slow, a.time+args.delay)
                swatList.append(ans)
        if args.json is not None:
            with open(args.json, "w") as outjson:
                json.dump(output, outjson, indent=2, cls=taup.DataClassJsonEncoder)
        if args.map is not None or args.showmap:
            mapplot(output, show=args.showmap)
        if args.slice is not None or args.showslice:
            sliceplot(output, show=args.showslice)




def do_parseargs():
    parser = argparse.ArgumentParser(
        description=f"""
        Find possible scatterers.
        Version={__version__}"""
    )
    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "-c",
        "--conf",
        help="Configuration as TOML",
        type=argparse.FileType("rb"),
    )
    parser.add_argument(
        "--eventdepth",
        help="event depth.",
        type=float,
        default=0
    )
    parser.add_argument(
        "--evt",
        help="event latitude and longitude.",
        type=float, nargs=2, required=True
    )
    parser.add_argument(
        "--sta",
        help="station latitude and longitude.",
        type=float, nargs=2, required=True
    )
    parser.add_argument(
        "-p","--phase", help="reference phase.",
        default="P"
    )
    parser.add_argument(
        "--delay",
        help="time delay of arrival relative to reference phase.",
        type=float, required=True
    )
    parser.add_argument(
        "--slow",
        help="observed slowness of suspected scatterer (s/deg)",
        type=float, required=True
    )
    parser.add_argument(
        "--model",
        help="earth model, as used by TauP.",
        default="prem"
    )
    parser.add_argument(
        "--taup",
        help="path to the TauP executable.",
        type=pathlib.Path
    )
    parser.add_argument(
        "--json",
        help="output to json file",
        type=pathlib.Path
    )
    parser.add_argument(
        "--map",
        help="output as matplotlib map",
        type=pathlib.Path
    )
    parser.add_argument(
        "--showmap",
        help="show matplotlib map to screen",
        action="store_true"
    )
    parser.add_argument(
        "--slice",
        help="output as matplotlib polar slice",
        type=pathlib.Path
    )
    parser.add_argument(
        "--showslice",
        help="show matplotlib polar slice to screen",
        action="store_true"
    )

    return parser.parse_args()



def main():

    args = do_parseargs()
    #conf = tomllib.load(args.conf)
    #args.conf.close()
    runswat(args)
    sys.exit(0)


if __name__ == "__main__":
    main()
