#! /bin/bash

# mkdir slow_7_time
for t in $(seq 4 1 20)
 do
  swat --evt 66 166 --eventdepth 300 --sta -11 120 --delay $t --slow 6 --bazoffset 0 5 --mindepth 50 --taup ../../../TauP-3.2.0-SNAPSHOT5/bin/taup --json slow_6_time/out_slow6_${t}s.json
done


#swat --evt 66 166 --eventdepth 300 --sta -11 120 --delay 0 --slow 5 --bazoffset 0 1 --mindepth 50 --taup ../../../TauP-3.2.0-SNAPSHOT5/bin/taup --map map_gcp.png
