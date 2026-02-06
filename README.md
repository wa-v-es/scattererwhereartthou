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

https://www.seis.sc.edu/downloads/TauP/prerelease/TauP-3.2.0-SNAPSHOT4.tgz

2) Probably put the TauP/bin on your path, although you can override this

3) Grab the latest taup_python package, here:

https://www.seis.sc.edu/downloads/TauP/prerelease/taup-0.2.0a1-py3-none-any.whl

4) create a conda environment, python>=3.11, install taup_python
```
conda create -n swat python=3.11
conda activate swat
pip install taup-0.2.0a1-py3-none-any.whl
```

5) checkout this repo, install it
```
git clone https://github.com/crotwell/scattererwhereartthou.git
cd scattererwhereartthou
pip install -v -e .
```

6) run the example tool
```
swat --evt -1 -101 --sta 34 -80 --delay 5 --map swat.png  --slow 8.0 --mindepth 500 --showmap
```

There are more options:
```
swat -h
usage: swat [-h] [-v] [-c CONF] [--eventdepth EVENTDEPTH] --evt EVT EVT --sta STA STA [-p PHASE] --delay DELAY --slow SLOW
            [--mindepth MINDEPTH] [--model MODEL] [--taup TAUP] [--json JSON] [--map MAP] [--showmap] [--slice SLICE]
            [--showslice]

Find possible scatterers. Version=0.0.1

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -c CONF, --conf CONF  Configuration as TOML
  --eventdepth EVENTDEPTH
                        event depth.
  --evt EVT EVT         event latitude and longitude.
  --sta STA STA         station latitude and longitude.
  -p PHASE, --phase PHASE
                        reference phase.
  --delay DELAY         time delay of arrival relative to reference phase.
  --slow SLOW           observed slowness of suspected scatterer (s/deg)
  --mindepth MINDEPTH   minimum depth of suspected scatterer (km)
  --model MODEL         earth model, as used by TauP.
  --taup TAUP           path to the TauP executable.
  --json JSON           output to json file
  --map MAP             output as matplotlib map
  --showmap             show matplotlib map to screen
  --slice SLICE         output as matplotlib polar slice
  --showslice           show matplotlib polar slice to screen
```

# Example

Say and earthquake is at (-1, -101) with depth 100 km and station at (34, -80). A possible scatterer is observed at 5 seconds after the P arrival with slowness 8.0 s/deg. This will show a map plot
of all the scatterers that can satisfy these values:

```
swat --evt -1 -101 --sta 34 -80 --delay 5 --slow 8.0 --eventdepth 100 --showmap
```

To see a slice view, change `--showmap` to `--showslice`:


```
swat --evt -1 -101 --sta 34 -80 --delay 5 --slow 8.0 --eventdepth 100 --showslice
```

and to save the raw data (very verbose...) to a json file:

```
swat --evt -1 -101 --sta 34 -80 --delay 5 --slow 8.0 --eventdepth 100 --json scatter.json
```

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

Each item in the `swat` list looks like this, with the parameters used first, then a list of actual possible scatterers:
```
{
      "eventdepth": 100.0,
      "evtstadeg": 40.173355,
      "toscatphase": "P,p,Ped",
      "fromscatphase": "P,p,Ped",
      "model": "prem",
      "evtlat": -1.0,
      "evtlon": -101.0,
      "stalat": 34.0,
      "stalon": -80.0,
      "rayparamdeg": 8.0,
      "traveltime": 450.98907,
      "mindepth": 50,
      "scatterers": [
        ...
        ]
```

The individual scatter points look like this, with
`scata` and `scatb` being the two off axis points:

```
{
          "scata": {
            "distdeg": 0.31043157,
            "depth": 55.00561,
            "time": 9.097412,
            "lat": 34.296383305372395,
            "lon": -79.88843545901085
          },
          "scata_az": 17.27160231877208,
          "scatb": {
            "distdeg": 0.31043157,
            "depth": 55.00561,
            "time": 9.097412,
            "lat": 34.198332544362046,
            "lon": -79.71160113092802
          },
          "scatb_az": -309.7900457686464,
          "C": 163.53082404370923,
          "es_baz": -146.25922172493713,
          ...
```

All this is subject to change!
