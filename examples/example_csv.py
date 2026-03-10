#!/usr/bin/env python

"""
Simple example of saving output to a CSV file.
"""

import csv
import taup
from scattererwhereartthou import SWAT, mapplot, sliceplot
import sys,re,os
import glob as glob

def extract_gridnumber(filename):
    match = re.search(r'gridnum(\d+)_', filename)
    if match:
        return int(match.group(1))
    return None

def extract_grid_nums(main_folder):
    pattern = os.path.join(main_folder, '*.jpg')

    # List to store the gridnum values
    gridnum_list = []
    for file_path in glob.glob(pattern):
    # Extract the filename from the file path
        filename = os.path.basename(file_path)

        # Use regex to find the number after 'gridnum'
        match = re.search(r'gridnum(\d+)', filename)
        if match:
            gridnum_list.append(int(match.group(1)))

    return(gridnum_list)
    
def extract_datapackfile(grid_number,folder_datapack):
    for file_name in os.listdir(folder_datapack):
        if file_name.endswith('.txt'):
            grid_num=extract_gridnumber(file_name)
            if grid_num==grid_number:
                # print(file_name)
                return file_name
###
def get_array_lat_long(eq_folder):
    folder='/Users/keyser/Research/AK_all_stations/sac_files/'+eq_folder+'/'
    folder_datapack=folder+'data_pack/'
    gridnum_list=extract_grid_nums(folder)
    #beam_deets '/Users/keyser/Research/sub_array_alaska/sac_files/230702_102743_PA/Datapack_20230702_1027_.05_.5Hz_60samps_Zcomp_WRHbase_gridnum2_num8_PP_Y_N_0.0_Y_-1.txt'
    patterns = {
        "Origin": re.compile(r"Origin: (\d+) (\d+) (\d+) (\d+):(\d+)"),
        "ArrCen": re.compile(r"ArrCen la/lo/elv: (\d+\.\d+) (-?\d+\.\d+) (\d+) Nst:(\d+)"),
        "ArrBaseStn": re.compile(r"ArrBaseStn: (\w+), grid la/lp (\d+), (-?\d+)"),
        "Event": re.compile(r"Event la/lo/dp: (-?\d+\.\d+) (-?\d+\.\d+) (\d+\.\d+)"),
        "Dist": re.compile(r"Dist: (\d+\.\d+)"),
        "Baz": re.compile(r"Baz \(Arr-Evt\): (\d+\.\d+)"),
        "Frequencies": re.compile(r"Frequencies: (\.\d+) - (\.\d+) Hz"),
        "TrcesSNR": re.compile(r"TrcesSNR mn,SD,min,max: (\d+\.\d+) (\d+\.\d+) (\d+\.\d+) (\d+\.\d+)"),
        "PredPP": re.compile(r"Pred PP \(prem\) time/U: (\d+\.\d+) (\d+\.\d+)")
    }

    # dictionary to store the extracted values
    deets_all=[]
    for grid_number in gridnum_list:
        beam_deets=folder_datapack+extract_datapackfile(grid_number,folder_datapack)

        deets = {
            "Origin": [],"ArrCen": [],"ArrBaseStn": [],"Event": [],"Dist": [],"Baz": [],"Frequencies": [],
            "TrcesSNR": [],"PredPP": []}

        # Read the file and match lines with the defined patterns
        with open(beam_deets, 'r') as file:
            for line in file:
                for key, pattern in patterns.items():
                    match = pattern.search(line)
                    if match:
                        # Handle ArrBaseStn separately to exclude non-numeric values
                        if key == "ArrBaseStn":
                            # Convert only numeric values, excluding the first group (station name)
                            deets[key].extend(match.groups()[1:])
                        else:
                            deets[key].extend(map(float, match.groups()))

        deets_all.append(deets)
    return deets_all
# location of taup version 3 executable, not needed if already on PATH
taup_path="../../TauP-3.2.0-SNAPSHOT6/bin/taup"

# -4.33 143.16 70.00 230402_180411_PA_inc2_r2.5
# la/lo/elv: 64.67 -155.88 362 TA (GSA) (grid 65, -157)
#dist=81.92
#P slow=5.238
#sP slow= 5.266
#PP slow= 8.23

deets_all= get_array_lat_long('230402_180411_PA_inc2_r2.5')
sys.exit()
model="iasp91"    # velocity model
evt=(-4.33, 143.16)   # eq lat, lon
eventdepth=70  # eq depth
sta=(64.67, -155.88)  # station lat, lon
phase="P"   # reference phase
max_dist_step=1.0 # max separation between path scatterers in degrees, default is 2 deg

# observed slownesses at station, usually p_minus, p, p_plus
# but can be more values for denser search results
# Note that the scatterer locations are quite sensitive to slowness, and so
# a denser gridsearch over slowness may be needed if the min-max range is large
# slownesses = [5.75+.05*p for p in range(-5, 6)]
slownesses = [5.75+.25*p for p in range(10)]
# slownesses= list(range(5.6, 8, .25))
# delay times relative to reference phase arrival, usually t_minus, t, t_plus
# but can be more values for denser search results
delaytimes = list(range(50, 171, 5))
# delaytimes=[50,55]
bazoffset=0
bazdelta=10
sta_scat_revphase="p,P,Ped,pP,PP"
evt_scat_phase="p,P,Ped,pP,PP"


with open("swat_230402_180411.csv", "w", newline='') as outcsv:
    csvwriter = csv.writer(outcsv)
    csvwriter.writerow(["scatlat", "scatlon", "scatdepth",
                        "scatdistdeg", "scatbaz", "sta_scat_p", "scat_time",
                        'sta_scat_phase','evt_scat_phase',
                        "evtlat", "evtlon", "evtdepth",
                        "stalat", "stalon",'baz_GCP'
                        ])
    with taup.TauPServer( taup_path=taup_path) as taupserver:
        print("starting...")
        # reference phase
        params = taup.PathQuery()
        params.model(model)
        params.event(*evt)
        params.sourcedepth(eventdepth)
        params.station(*sta)
        params.phase(phase)
        timeResult = params.calc(taupserver)

        swatList = []
        swat = SWAT(taupserver, eventdepth, model=model,
            sta_scat_revphase=sta_scat_revphase,
            evt_scat_phase=evt_scat_phase)
        swat.event(*evt)
        swat.station(*sta)
        swat.dist_step = max_dist_step

        for a in timeResult.arrivals:
            print(f"Arrival: {a}")
            traveltimes = [a.time+delay for delay in delaytimes]
            print(f"slow: {slownesses}  delay: {delaytimes} traveltimes: {traveltimes}")
            ans = swat.find_via_path(slownesses, traveltimes, bazoffset=bazoffset, bazdelta=bazdelta)
            swatList.append(ans)
            for sc in ans.scatterers:
                csvwriter.writerow([format(sc.scat.lat, "0.3f"), format(sc.scat.lon, "0.3f"),
                                    format(sc.scat.depth, "0.3f"),
                                    format(sc.scat.distdeg, "0.2f"),
                                    format(sc.scat_baz, "0.3f"),
                                    format(sc.sta_scat_rayparam, "0.2f"),
                                    format(sc.scat.time+sc.evt_scat.time, "0.2f"),
                                    sc.sta_scat_phase,sc.evt_scat.phase,
                                    ans.evtlat, ans.evtlon, ans.evtdepth,
                                    ans.stalat, ans.stalon,format(ans.esbaz, "0.3f")
                                    ])
