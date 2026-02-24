#! /bin/bash

mkdir slow_5_time
for t in $(seq 0.05 .05 .1)
 do
  swat --evt 66 166 --eventdepth 0 --sta -11 120 --delay $t --slow 5.087 --taup ../../../TauP-3.2.0-SNAPSHOT6/bin/taup --json slow_5_time/out_slow5_${t}s.json
done


#swat --evt 66 166 --eventdepth 300 --sta -11 120 --delay 0 --slow 5 --bazoffset 0 1 --mindepth 50 --taup ../../../TauP-3.2.0-SNAPSHOT5/bin/taup --map map_gcp.png

swat --evt -17.8800 -174.9500 --eventdepth 229 --sta 65.7000 -149.6200 --delay 82.93 --slow .604 --bazoffset -12 1 --mindepth 100 --taup ../../../TauP-3.2.0-SNAPSHOT6/bin/taup
