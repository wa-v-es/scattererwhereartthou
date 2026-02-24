
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
        timeResult = params.calc(taupserver)
        swatList = []
        output = {
            "taup": timeResult,
            "swat": swatList
        }

        if len(timeResult.arrivals) == 0:
            print(f"No arrivals for {ref_phase} for {evtlat},{evtlon} ({eventdepth} km) to {stalat},{stalon}")
        else:
            for a in timeResult.arrivals:
                if args.verbose:
                    print(f"Arrival: {a}")
                swat = SWAT(taupserver, args.eventdepth,
                            evt_scat_phase=args.evtscatphase,
                            sta_scat_revphase=args.stascatphase,
                            model=args.model)
                if args.mindepth is not None:
                    swat.minDepth(args.mindepth)
                swat.event(evtlat, evtlon)
                swat.station(stalat, stalon)
                obs_baz_offset = args.bazoffset[0]
                obs_baz_delta = args.bazoffset[1]
                traveltimes = [a.time+delay for delay in args.delay]
                ans = swat.find_via_path(args.slow,
                                         traveltimes,
                                         bazoffset=obs_baz_offset,
                                         bazdelta=obs_baz_delta)
                swatList.append(ans)
        if args.json is not None:
            with open(args.json, "w") as outjson:
                json.dump(output, outjson, indent=2, cls=taup.DataClassJsonEncoder)
        if args.map is not None or args.showmap:
            mapplot(swatList, tauptimes=timeResult, show=args.showmap)
        if args.slice is not None or args.showslice:
            sliceplot(swatList, tauptimes=timeResult, show=args.showslice)
        if args.text or not(args.json or args.map or args.slice or args.showmap or args.showslice ):
            if args.text:
                outf = open(args.text, "w")
            else:
                outf = sys.stdout
            print(f" Lat   Lon   Depth Dist   Baz", file=outf)
            for s in swatList:
                for scat in s.scatterers:
                    pt = scat.scat
                    baz = scat.scat_baz
                    print(f"{pt.lat:.2f} {pt.lon:.2f} {pt.depth:.1f} {pt.distdeg:.2f} {baz:.1f}", file=outf)
            if args.text:
                outf.close()



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
        help="event depth in km.",
        type=float,
        default=0,
        metavar='d',
    )
    parser.add_argument(
        "--evt",
        help="event latitude and longitude.",
        type=float, nargs=2, required=True, metavar=('lat', 'lon')
    )
    parser.add_argument(
        "--sta",
        help="station latitude and longitude.",
        type=float, nargs=2, required=True, metavar=('lat', 'lon')
    )
    parser.add_argument(
        "-p","--phase", help="reference phase.",
        default="P"
    )
    parser.add_argument(
        "--delay",
        help="time delays of arrival relative to reference phase.",
        nargs='+',
        type=float, required=True, metavar="s"
    )
    parser.add_argument(
        "--bazoffset",
        help="observed back azimuth offset of the scatterer relative to the reference phase and plus minus range.",
        type=float,
        nargs=2,
        default=[0, 180], metavar=('offset', 'delta')
    )
    parser.add_argument(
        "--slow",
        help="observed slowness of suspected scatterer (s/deg)",
        type=float, nargs='+',
        required=True, metavar='p'
    )
    parser.add_argument(
        "--mindepth",
        help="minimum depth of suspected scatterer (km)",
        type=float, default=50, metavar='d'
    )
    parser.add_argument(
        "--model",
        help="earth model, as used by TauP.",
        default="prem", metavar='name'
    )
    parser.add_argument(
        "--stascatphase",
        help="list of reversed phases from the station to the scatterer.",
        default="p,P,Ped", metavar='phase'
    )
    parser.add_argument(
        "--evtscatphase",
        help="list of phases from the earthquake to the scatterer.",
        default="p,P,Ped", metavar='phase'
    )
    parser.add_argument(
        "--taup",
        help="path to the TauP executable.",
        type=pathlib.Path
    )
    parser.add_argument(
        "--json",
        help="output to json file",
        type=pathlib.Path, metavar="name.json"
    )
    parser.add_argument(
        "--text",
        help="output points as text to a file",
        type=pathlib.Path, metavar="name.txt"
    )
    parser.add_argument(
        "--map",
        help="output as matplotlib map",
        type=pathlib.Path, metavar="map.png"
    )
    parser.add_argument(
        "--showmap",
        help="show matplotlib map to screen",
        action="store_true"
    )
    parser.add_argument(
        "--slice",
        help="output as matplotlib polar slice",
        type=pathlib.Path, metavar="slice.png"
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
