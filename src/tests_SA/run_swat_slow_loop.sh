#! /bin/bash

mkdir slow_5_time
for t in $(seq 0 1 2)
 do
  swat --evt 66 166 --eventdepth 300 --sta -11 120 --delay $t --slow 5 --bazoffset 0 2 --mindepth 50 --taup ../../../TauP-3.2.0-SNAPSHOT5/bin/taup --json slow_5_time/out_slow5_${t}s.json
done


#swat --evt 66 166 --eventdepth 300 --sta -11 120 --delay 0 --slow 5 --bazoffset 0 1 --mindepth 50 --taup ../../../TauP-3.2.0-SNAPSHOT5/bin/taup --map map_gcp.png
