# scattererwhereartthou
Find possible scatterers from slowness and back azimuth

The basic idea is to shoot a ray from the station with the known ray param. Then consider each point along the path as if it is a potential scatterer. Then, check to see if a ray from that scatterer with the residual travel time can arrive at the earthquake location, and with travel distance large enough that a triangle is possible. If so, calculate the lat,lon that the scatterer would need to be at in order to have the correct distance to the earthquake and station via a little spherical geometry.

# Requirement
This makes use of the TauP Toolkit for the path and time calculations and the version must be > 3.2.0.

# Install
I assume you are on a vaguely *nix like system, are using conda,
and can do normal download and install activities.

1) Install version 3.2.0-snapshot4 or greater of the TauP Toolkit.
This is available here:

https://www.seis.sc.edu/downloads/TauP/prerelease/TauP-3.2.0-SNAPSHOT5.tgz

2) Probably put the TauP/bin on your path, although you can override this

3) Grab the latest taup_python package, here:

https://www.seis.sc.edu/downloads/TauP/prerelease/taup-0.2.0a3-py3-none-any.whl

4) create a conda environment, python>=3.11, install taup_python
```
conda create -n swat python=3.13 -y
conda activate swat
pip install taup-0.2.0a3-py3-none-any.whl
```

5) checkout this repo, install it
```
git clone https://github.com/crotwell/scattererwhereartthou.git
cd scattererwhereartthou
pip install -v -e .
```

6) run the example tool
```
swat --evt -1 -101 --sta 34 -80 --delay 5 --slow 8.0 --bazoffset 5 1
```

There are more options:
```
swat -h
usage: swat [-h] [-v] [-c CONF] [--eventdepth d] --evt lat lon --sta lat lon [-p PHASE] --delay s [--bazoffset offset delta]
            --slow p [--mindepth d] [--model name] [--taup TAUP] [--json name.json] [--text name.txt] [--map map.png] [--showmap]
            [--slice slice.png] [--showslice]

Find possible scatterers. Version=0.0.1

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -c CONF, --conf CONF  Configuration as TOML
  --eventdepth d        event depth in km.
  --evt lat lon         event latitude and longitude.
  --sta lat lon         station latitude and longitude.
  -p PHASE, --phase PHASE
                        reference phase.
  --delay s             time delay of arrival relative to reference phase.
  --bazoffset offset delta
                        observed back azimuth offset of the scatterer relative to the reference phase and plus minus range.
  --slow p              observed slowness of suspected scatterer (s/deg)
  --mindepth d          minimum depth of suspected scatterer (km)
  --model name          earth model, as used by TauP.
  --taup TAUP           path to the TauP executable.
  --json name.json      output to json file
  --text name.txt       output points as text to a file
  --map map.png         output as matplotlib map
  --showmap             show matplotlib map to screen
  --slice slice.png     output as matplotlib polar slice
  --showslice           show matplotlib polar slice to screen
```

# Example

Say and earthquake is at (-1, -101) with depth 100 km and station at (34, -80). A possible scatterer is observed at 5 seconds after the P arrival with slowness 8.0 s/deg. This will show a map plot
of all the scatterers that can satisfy these values:

```
swat --evt -1 -101 --sta 34 -80 --delay 5 --slow 8.0 --eventdepth 100 --showmap
```

For a textual output of the scatterer points, limiting them to
within +-1 deg of a -4 degree back azimuth offset:
```
swat --evt -1 -101 --sta 34 -80 --delay 5 --slow 8.0 --eventdepth 100 --bazoffset -4 1
```

To see a slice view, change `--showmap` to `--showslice`:


```
swat --evt -1 -101 --sta 34 -80 --delay 5 --slow 8.0 --eventdepth 100 --showslice
```

and to save the raw data (very verbose...) to a json file:

```
swat --evt -1 -101 --sta 34 -80 --delay 5 --slow 8.0 --eventdepth 100 --json scatter.json
```

The optional `--bazoffset <value> <delta>` argument will limit
scatterers with back azimuth to be the given value relative to the
reference phase, plus or minus the delta. If the reference phase back
azimuth (station to event) is 100, then `--bazoffset 5 2` will find
scatterers between 103 and 107 degrees.

The saved data looks like:
```
{
  "taup": {
    ...
  },
  "swat": [
  ...
  ]
}
```

where the `taup` section is TauP's result for the reference phase, and `swat` contains the possible scatterers.

Each item in the `swat` list looks like this, with the parameters used first, then a list of actual possible scatterers. `backrays` is the result of taup path with the
given ray parameter leaving the station, shooting the observed ray parameter
backwards from the station.

```
"swat": [
    {
      "eventdepth": 100.0,
      "esdistdeg": 40.17335524279465,
      "esaz": 27.42246100424842,
      "esbaz": -146.25922172493713,
      "toscatphase": "P,p,Ped",
      "fromscatphase": "P,p,Ped",
      "model": "prem",
      "evtlat": -1.0,
      "evtlon": -101.0,
      "stalat": 34.0,
      "stalon": -80.0,
      "rayparamdeg": 8.0,
      "traveltime": 450.98907,
      "mindepth": 600.0,
      "scatterers": [
        ...
        ],
      "backrays": {
        ...
      }
```

The individual scatter points look like this, with
`scat` the scattering point and `scat_baz` the back azimuth from the station
to the scatterer. `baz_offset` is the shift in back azimuth needed
to satisfy the arrival time projecting back to the earthquake from the
scatterer. `scat_evt` is the travel time information from the scatterer
back to the event.

```
{
          "scat": {
            "distdeg": 5.1766777,
            "depth": 600.0,
            "time": 93.68801,
            "lat": 31.31577117505093,
            "lon": -85.25918119945892
          },
          "scat_baz": -119.78523118292273,
          "baz_offset": 26.47399054201441,
          "scat_evt": {
            "sourcedepth": 600.0,
            "receiverdepth": 100.0,
            "distdeg": 35.60188,
            "phase": "P",
            "time": 357.30106,
            "rayparam": 8.185079,
            "takeoff": 55.63494,
            "incident": 37.09249,
            "puristdist": 35.60188,
            "puristname": "P",
            "desc": null,
            "amp": null,
            "scatter": null,
            "relative": null,
            "derivative": null,
            "pierce": [],
            "pathlength": null,
            "pathSegments": []
          }
        }
```

All this is subject to change!
