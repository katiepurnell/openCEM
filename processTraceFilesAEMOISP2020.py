# File to process AEMO ISP2020 Trace data files into mySQL format & import into new tables
# yyyy/mm/dd hh:mm:ss

# Import modules
from pathlib import Path
import pandas as pd
import os
import re
import datetime as dt
from datetime import datetime, date, timedelta

#Name constants
base_path = Path("E:/OneDrive - UNSW/PhD/Modelling/openCEMKP/database local replica october 2020/ISP Traces/")
state_list = ["NSW","QLD","VIC","SA","TAS"]
state_dict = {"NSW":1,"QLD":2,"SA":3,"TAS":4,"VIC":5}
demand_scenario_list = ["Central"]#,"StepChange"]
demand_scenario_dict = {"Central":7,"StepChange":10}
tech_type_list = ["WL"]#,"WH","WOS","SAT","CST"] #
tech_type_dict = {"SAT":11,"CST":13,"WH":17,"WL":12,"WOS":30}

rez_list = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8","N1","N2","N3","N4","N5","N6","N7","N8","N9","V1","V2","V3","V4","V5","V6","S1","S2","S3","S4","S5","S6","S7","S8","S9","T1","T2","T3"]
rez_dict_name: {"Q1":"Far North Queensland","Q2":"North Queensland Clean Energy Hub","Q3":"Northern Queensland","Q4":"Isaac","Q5": "Barcaldine","Q6":"Fitzroy","Q7":"Wide Bay","Q8":"Darling Downs","N1":"North West New South Wales","N2":"New England","N3":"Central-West Orana","N4":"Southern New South Wales Tablelands","N5":"Broken Hill","N6":"South West New South Wales","N7":"Wagga Wagga","N8":"Tumut","N9":"Cooma-Monaro","V1":"Ovens Murray","V2":"Murray River","V3":"Western Victoria","V4":"South West Victoria","V5":"Gippsland","V6":"Central North Victoria","S1":"South East SA","S2":"Riverland","S3":"Mid-North SA","S4":"Yorke Peninsula","S5":"Northern SA","S6":"Leigh Creek","S7":"Roxby Downs","S8":"Eastern Eyre Peninsula","S9":"Western Eyre Peninsula","T1":"North East Tasmania","T2":"North West Tasmania","T3":"Tasmania Midlands"}

rez_dict_ntndp_zone = {"Q1":1,"Q2":1,"Q3":1,"Q4":1,"Q5":2,"Q6":2,"Q7":4,"Q8":3,"N1":8,"N2":8,"N3":7,"N4":7,"N5":5,"N6":5,"N7":5,"N8":6,"N9":6,"V1":12,"V2":11,"V3":11,"V4":10,"V5":9,"V6":12,"S1":15,"S2":13,"S3":13,"S4":13,"S5":13,"S6":13,"S7":13,"S8":13,"S9":13,"T1":16,"T2":16,"T3":16}

# OPSO: Contains half-hourly regional demand traces for operational demand (demand after the impact of rooftop PV and PVNSG)
# OPSO_PVLITE: Contains half-hourly regional demand traces for operational demand (demand before the impact of rooftop PV and PVNSG)
# PV: Contains half hourly regional generation traces for rooftop PV
# PV_TOT: Contains half hourly regional generation traces for all embedded PV, including rooftop PV and PVNSG
# EV: Contains half hourly regional aggregate electric vehicle charging
# ESS: Contains half hourly regional aggregate customer installed battery charging/discharging.
# VTOH: Contains half hourly regional aggregate discharging from electric vehicles to homes (only used in the Step change scenario).
# POE10 = prob. of exceedance = 10% vs POE50 = 50%. We use POE 10 for everything = more worse case scenario (lower prob of being higher than this)

# DEMAND_AND_ROOFTOP_TRACES FROM AEMO ISP TO MYSQL FORMAT
def statesToLinear(state,demand_scenario):
    input_path = Path(base_path/demand_scenario/state)
    output_path = Path(base_path/demand_scenario)

    if demand_scenario == "Central":
        # demand_50 = state + "_RefYear_2019_Neutral_POE50_OPSO.csv"
        demand_fn = state + "_RefYear_2019_Neutral_POE10_OPSO.csv"
        # demand_less_pv = state + "_RefYear_2019_Neutral_POE10_OPSO_PVLITE.csv"
        pv_fn = state + "_RefYear_2019_Neutral_POE10_PV.csv"
        pv_tot_fn = state + "_RefYear_2019_Neutral_POE10_PV_TOT.csv"
        # vtoh = state + "_RefYear_2019_Neutral_POE50_RES_VTOH.csv"
        ev_fn = state + "_RefYear_2019_Neutral_POE10_EV.csv"
        ess_fn = state + "_RefYear_2019_Neutral_POE10_ESS.csv"
    elif demand_scenario == "StepChange":
        # demand_50 = state + "_RefYear_2019_Strong_POE50_OPSO.csv"
        demand_fn = state + "_RefYear_2019_Strong_POE10_OPSO.csv"
        # demand_less_pv = state + "_RefYear_2019_Strong_POE10_OPSO_PVLITE.csv"
        pv_fn = state + "_RefYear_2019_Strong_POE10_PV.csv"
        pv_tot_fn = state + "_RefYear_2019_Strong_POE10_PV_TOT.csv"
        vtoh_fn = state + "_RefYear_2019_Strong_POE10_RES_VTOH.csv" # Only exists in Step Change
        ev_fn = state + "_RefYear_2019_Strong_POE10_EV.csv"
        ess_fn = state + "_RefYear_2019_Strong_POE10_ESS.csv"

    # Export Names
    demand_fn_export = state+"_"+demand_scenario+"_opso_poe10.csv"
    pv_fn_export = state+"_"+demand_scenario+"_pv.csv"
    pv_tot_fn_export = state+"_"+demand_scenario+"_pv_tot.csv"
    ev_fn_export = state+"_"+demand_scenario+"_ev.csv"
    ess_fn_export = state+"_"+demand_scenario+"_ess.csv"
    vtoh_fn_export = state+"_"+demand_scenario+"_vtoh.csv"

    # Check if traces already consolidated for the state
    try:
        demand_state = pd.read_csv(output_path/demand_fn_export)
        pv_state = pd.read_csv(output_path/pv_fn_export)
        pv_tot_state = pd.read_csv(output_path/pv_tot_fn_export)
        ev_state = pd.read_csv(output_path/ev_fn_export)
        ess_state = pd.read_csv(output_path/ess_fn_export)
        if demand_scenario == "StepChange":
            vtoh_state = pd.read_csv(output_path/vtoh_fn_export)

    except FileNotFoundError: # Make the state traces
        try:
            demand = pd.read_csv(input_path/demand_fn)
            convertTimeSeries(demand,demand_fn_export,output_path)
            pv = pd.read_csv(input_path/pv_fn)
            convertTimeSeries(pv,pv_fn_export,output_path)
            pv_tot = pd.read_csv(input_path/pv_tot_fn)
            convertTimeSeries(pv_tot,pv_tot_fn_export,output_path)
            ev = pd.read_csv(input_path/ev_fn)
            convertTimeSeries(ev,ev_fn_export,output_path)
            ess = pd.read_csv(input_path/ess_fn)
            convertTimeSeries(ess,ess_fn_export,output_path)
            if demand_scenario == "StepChange":
                vtoh = pd.read_csv(input_path/vtoh_fn)
                convertTimeSeries(vtoh,vtoh_fn_export,output_path)

        except FileNotFoundError:
            print("--- raw AEMO files not found for {} - please download them from https://www.aemo.com.au/energy-systems/major-publications/integrated-system-plan-isp/2020-integrated-system-plan-isp/2019-isp-database".format(demand_scenario))

    return
def combineStateTraces(state,demand_scenario):
    output_path = Path(base_path/demand_scenario)
    state_master_df = pd.DataFrame()
    # cols = ["id","region_id","demand_scenario_id","timestamp","source_id","ess","ev","opso_poe10","opso_poe50","pv","pv_tot","vtoh"]

    # Export Names
    demand_fn_export = state+"_"+demand_scenario+"_opso_poe10.csv"
    pv_fn_export = state+"_"+demand_scenario+"_pv.csv"
    pv_tot_fn_export = state+"_"+demand_scenario+"_pv_tot.csv"
    ev_fn_export = state+"_"+demand_scenario+"_ev.csv"
    ess_fn_export = state+"_"+demand_scenario+"_ess.csv"
    vtoh_fn_export = state+"_"+demand_scenario+"_vtoh.csv"

    # Check if traces already consolidated for the state
    try:
        demand_state = pd.read_csv(output_path/demand_fn_export, index_col = "timestamp", parse_dates=True)
        demand_state.rename(columns={"Data" : "opso_poe10"}, inplace=True)
        pv_state = pd.read_csv(output_path/pv_fn_export, index_col = "timestamp", parse_dates=True)
        pv_state.rename(columns={"Data" : "pv"}, inplace=True)
        pv_tot_state = pd.read_csv(output_path/pv_tot_fn_export, index_col = "timestamp", parse_dates=True)
        pv_tot_state.rename(columns={"Data" : "pv_tot"}, inplace=True)
        ev_state = pd.read_csv(output_path/ev_fn_export, index_col = "timestamp", parse_dates=True)
        ev_state.rename(columns={"Data" : "ev"}, inplace=True)
        ess_state = pd.read_csv(output_path/ess_fn_export, index_col = "timestamp", parse_dates=True)
        ess_state.rename(columns={"Data" : "ess"}, inplace=True)
        if demand_scenario == "StepChange":
            vtoh_state = pd.read_csv(output_path/vtoh_fn_export, index_col = "timestamp", parse_dates=True)
            vtoh_state.rename(columns={"Data" : "vtoh"}, inplace=True)

        # Merge these columns on the timestamp index
        state_master_df = demand_state.merge(pv_state, how='inner', left_index=True, right_index=True)
        state_master_df = state_master_df.merge(pv_tot_state, how='inner', left_index=True, right_index=True)
        state_master_df = state_master_df.merge(ev_state, how='inner', left_index=True, right_index=True)
        state_master_df = state_master_df.merge(ess_state, how='inner', left_index=True, right_index=True)
        if demand_scenario == "StepChange":
            state_master_df = state_master_df.merge(vtoh_state, how='inner', left_index=True, right_index=True)

        state_master_df["source_id"] = 3
        state_master_df["demand_scenario_id"] = demand_scenario_dict.get(demand_scenario)
        state_master_df["region_id"] = state_dict.get(state)

        # Export
        master_fn = "1_master_"+state+"_"+demand_scenario+".csv"
        state_master_df.to_csv(output_path/master_fn)


    except FileNotFoundError: # Make the state traces
        print("Timeseries, state files not found for {} {} - please do this first".format(state, demand_scenario))

    return

# WIND_AND_SOLAR_TRACES FROM AEMO ISP TO MYSQL FORMAT
def rezZonesToLinear(tech_type):
    if tech_type in ["SAT","CST"]:
        input_path = Path(base_path/"ISP Solar Traces r2019")
    elif tech_type in ["WH","WL","WOS"]:
        input_path = Path(base_path/"ISP Wind Traces r2019")
    output_path = Path(base_path)

    # Gather names of all files for that tech type
    fn_list = []
    completed_list = []
    for i in os.listdir(input_path):
        if (i.find("_"+tech_type+"_") != -1):
            fn_list.append(i)
    completed_list = [filename for filename in os.listdir(input_path) if filename.startswith("1_"+tech_type+"_")]
    fn_list = [k for k in fn_list if k not in completed_list]
    print(fn_list)

    for fn in fn_list:
        print(fn)
        if tech_type in ["SAT","CST"]:
            left = "REZ_"
            right = "_"+tech_type+"_"
            rez = fn[fn.index(left)+len(left):fn.index(right)]
        elif tech_type in ["WH","WL","WOS"]:
            right = "_"+tech_type+"_"
            rez = fn.split(right)[0]
        print(rez)
        left = tech_type+"_"
        right = "_RefYear2019"
        name = fn[fn.index(left)+len(left):fn.index(right)]
        print(name)

        # Check if traces already consolidated for the state
        try:
            fn_export = "1_" + tech_type + "_" + rez +"_"+name +".csv"
            finished_df = pd.read_csv(input_path/fn_export)
        except FileNotFoundError: # Make the state traces
            df = pd.read_csv(input_path/fn)
            convertTimeSeriesWS(df,fn_export,input_path, rez, name)

    return
def combineREZTraces(tech_type):
    if tech_type in ["SAT","CST"]:
        input_path = Path(base_path/"ISP Solar Traces r2019")
    elif tech_type in ["WH","WL","WOS"]:
        input_path = Path(base_path/"ISP Wind Traces r2019")

    # Gather names of all files for that tech type
    completed_list = []
    completed_tech_list = [filename for filename in os.listdir(input_path) if filename.startswith("1_"+tech_type+"_")]

    master_tech = pd.DataFrame()
    for rez in rez_list:
        print(rez)
        completed_tech_list_per_rez = [filename for filename in completed_tech_list if filename.startswith("1_"+tech_type+"_"+rez)]
        print(completed_tech_list_per_rez)

        master_tech_rez = pd.DataFrame()
        for f in completed_tech_list_per_rez:
            num = completed_tech_list_per_rez.index(f)
            print("---{}/{}: {}".format(num,len(completed_tech_list_per_rez),f))
            file_df = pd.read_csv(input_path/f, index_col = "timestamp", parse_dates=True)
            file_df = file_df.rename(columns={"Data" : str(num)})
            file_df = file_df.drop(["name"],axis=1)
            # print(file_df)
            if f == completed_tech_list_per_rez[0]:
                master_tech_rez = file_df.copy()
            else:
                file_df = file_df.drop(["rez"],axis=1)
                master_tech_rez = master_tech_rez.merge(file_df, how='inner', left_index=True, right_index=True)

        # print(master_tech_rez)
        # Average the columns 0 -> len(completed_tech_list_per_rez)
        if len(completed_tech_list_per_rez)>1:
            # print("----More than one entry for this rez and this tech")
            # cols =  [i for i in range(len(completed_tech_list_per_rez))]
            cols = [str(i) for i in range(len(completed_tech_list_per_rez))]
            # print(cols)
            # print(master_tech_rez[cols])
            # dcols = master_tech_rez[cols]
            master_tech_rez['mw'] = master_tech_rez[cols].mean(axis=1)
            # print(master_tech_rez)
            master_tech_rez = master_tech_rez.drop(cols,axis=1)
        else:
            master_tech_rez = master_tech_rez.rename(columns={"0" : "mw"})

        # print(master_tech_rez)
        master_tech_rez["ntndp_zone_id"] = rez_dict_ntndp_zone.get(rez)

        if rez == rez_list[0]:
            master_tech = master_tech_rez.copy()
        else:
            master_tech = master_tech.append(master_tech_rez, ignore_index=False)


    master_tech["technology_type_id"] = tech_type_dict.get(tech_type)
    master_tech["source_id"] = 3
    # print(master_tech)

    export_name = "1_w_and_s_tech_"+tech_type+".csv"
    master_tech.to_csv(base_path/export_name)

    return

# COMMON FUNCTIONS
def datetime_range(start, end, delta):
    current = start
    if not isinstance(delta, timedelta):
        delta = timedelta(**delta)
    while current < end:
        yield current
        current += delta
def convertTimeSeries(db,final_db_name,final_db_path):
    print("Converting {}".format(final_db_name))
    # For each row in the new df, create datetime using the year, month, day columns and a time corresponding to 1,2,3 etc half hour periods, transpose this data and put in the new df
    db["Date"] = pd.to_datetime([f'{y}-{m}-{d}' for y, m, d in zip(db.Year, db.Month, db.Day)])
    master_db = pd.DataFrame()
    for row in range(0,len(db)): #range(0,2):#
        start = db.loc[row,"Date"]
        end = db.loc[row,"Date"] + timedelta(days=1)
        timeseries = pd.Series(datetime_range(start, end, {'hours':0.5})).rename("timestamp")
        single_day = db.iloc[row,:].drop(["Year","Month","Day","Date"],axis=0)
        single_day_t = pd.DataFrame(single_day.transpose().rename("Data")).reset_index(drop=True) #

        daily_df = pd.concat([timeseries, single_day_t], axis=1).reset_index(drop=True)
        daily_df = daily_df.set_index("timestamp")#,drop=True,inplace=True)
        # Append new row to existing df
        if row == 0:
            master_db = daily_df.copy()
        else:
            master_db = master_db.append(daily_df, ignore_index=False)
        row = row + 1

    # Export this db
    master_db.to_csv(final_db_path/final_db_name)
    return

def convertTimeSeriesWS(db,final_db_name,final_db_path,rez,name):
    print("Converting {}".format(final_db_name))
    # For each row in the new df, create datetime using the year, month, day columns and a time corresponding to 1,2,3 etc half hour periods, transpose this data and put in the new df
    db["Date"] = pd.to_datetime([f'{y}-{m}-{d}' for y, m, d in zip(db.Year, db.Month, db.Day)])
    # print(db)
    master_db = pd.DataFrame()
    for row in range(0,len(db)): #range(0,2):#
        start = db.loc[row,"Date"]
        end = db.loc[row,"Date"] + timedelta(days=1)
        # print(start)
        # print(end)
        timeseries = pd.Series(datetime_range(start, end, {'hours':0.5})).rename("timestamp")
        # print(timeseries)
        single_day = db.iloc[row,:].drop(["Year","Month","Day","Date"],axis=0)
        single_day_t = pd.DataFrame(single_day.transpose().rename("Data")).reset_index(drop=True) #
        # print(single_day_t)
        daily_df = pd.concat([timeseries, single_day_t], axis=1).reset_index(drop=True)
        daily_df = daily_df.set_index("timestamp")#,drop=True,inplace=True)
        daily_df["rez"] = rez
        daily_df["name"] = name
        # print(daily_df)
        # Append new row to existing df
        if row == 0:
            master_db = daily_df.copy()
        else:
            master_db = master_db.append(daily_df, ignore_index=False)
        # print(master_db)
        row = row + 1

    # Export this db
    master_db.to_csv(final_db_path/final_db_name)
    return


#################### RUN SCRIPT #########################
# for demand_scenario in demand_scenario_list:
#     for state in state_list:
        # statesToLinear(state,demand_scenario)
        # combineStateTraces(state,demand_scenario)

for tech_type in tech_type_list:
    print("\n {}".format(tech_type))
    # rezZonesToLinear(tech_type)
    combineREZTraces(tech_type)
