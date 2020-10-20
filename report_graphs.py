## Consolidate the traces & results output by opencem inot more useable forms

# Import modules
from pathlib import Path
import pandas as pd
import os

#Name constants
# scen_name = "test_evs_dumb"
scen_list = ["test_bau","test_evs_dumb","test_evs_smart_0fit","test_evs_v2g_0fit","test_evs_v2g_100fit"]
yearlist = ["2021","2026","2031","2036","2041","2046","2050"]
zonelist = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
regionlist = [1,2,3,4,5]
base_path = Path("E:/OneDrive - UNSW/PhD/Modelling/openCEMKP/scenarios/")

# Consolidate results to be single sheet -> years columns, merge to have same rows
def consolidateResults(scen_name):
    results_path = Path(base_path/scen_name/"results")
    output_path = Path(base_path/scen_name)
    master_results_file = pd.DataFrame()
    for y in yearlist:
        # print(y)
        filename = scen_name + "_results_"+str(y)+".csv"
        try:
            year_results = pd.read_csv(results_path/filename)
            # print(year_results)
        except FileNotFoundError:
            print("--- scen: {} for {} not found - skipping".format(scen_name,y))
            continue
        # year_results.index = pd.to_datetime(year_results.index)
        year_result_t = year_results.transpose()
        year_result_t.columns =[y]
        # print(year_result_t)

        if y == yearlist[0]:
            master_results_file = year_result_t.copy()
        else:  # Merge with master
            master_results_file = pd.merge(master_results_file, year_result_t, how='outer', left_index=True, right_index=True)
        # print(master_results_file)

    # Export
    fn_out = scen_name+"_results.csv"
    master_results_file.to_csv(output_path/fn_out)

    return

# Consolidate traces (EVs) to have years in separate tabs (in same workbook)
def consolidateEVTraces(scen_name):
    results_path = Path(base_path/scen_name/"results")
    output_path = Path(base_path/scen_name)
    for y in yearlist:
        try:
            fn = scen_name + str(y) + "_charge_z1.csv" # test file
            fn_read_test = pd.read_csv(results_path/fn)
        except FileNotFoundError:
            print("No ev traces for {} in {}".format(scen_name,y))
            continue

        # EV traces -> all zones consolidated into yearly xlsx file
        charge_fn_xlsx = "1_"+scen_name + "_ev_total_charge_allz"+str(y)+".xlsx"
        with pd.ExcelWriter(results_path/charge_fn_xlsx) as writer:
            for zone in zonelist:
                charge_fn = scen_name + str(y) + "_charge_z"+str(zone)+".csv"
                charge_zone = pd.read_csv(results_path/charge_fn)
                charge_zone.index = pd.to_datetime(charge_zone.index)
                charge_zone.to_excel(writer, sheet_name=str(zone), index=True)
        dcharge_fn_xlsx = "1_"+scen_name + "_ev_dumb_charge_allz"+str(y)+".xlsx"
        with pd.ExcelWriter(results_path/dcharge_fn_xlsx) as writer:
            for zone in zonelist:
                dcharge_fn = scen_name + str(y) + "_dumbcharge_z"+str(zone)+".csv"
                dumb_charge_zone = pd.read_csv(results_path/dcharge_fn)
                dumb_charge_zone.index = pd.to_datetime(dumb_charge_zone.index)
                dumb_charge_zone.to_excel(writer, sheet_name=str(zone), index=True)
        scharge_fn_xlsx = "1_"+scen_name + "_ev_smart_charge_allz"+str(y)+".xlsx"
        with pd.ExcelWriter(results_path/scharge_fn_xlsx) as writer:
            for zone in zonelist:
                scharge_fn = scen_name + str(y) + "_smartcharge_z"+str(zone)+".csv"
                smart_charge_zone = pd.read_csv(results_path/scharge_fn)
                smart_charge_zone.index = pd.to_datetime(smart_charge_zone.index)
                smart_charge_zone.to_excel(writer, sheet_name=str(zone), index=True)
        con_fn_xlsx = "1_"+scen_name + "_ev_connected_allz"+str(y)+".xlsx"
        with pd.ExcelWriter(results_path/con_fn_xlsx) as writer:
            for zone in zonelist:
                con_fn = scen_name + str(y) + "_evconnected_z"+str(zone)+".csv"
                con_zone = pd.read_csv(results_path/con_fn)
                con_zone.index = pd.to_datetime(con_zone.index)
                con_zone.to_excel(writer, sheet_name=str(zone), index=True)
        level_fn_xlsx = "1_"+scen_name + "_ev_level_allz"+str(y)+".xlsx"
        with pd.ExcelWriter(results_path/level_fn_xlsx) as writer:
            for zone in zonelist:
                level_fn = scen_name + str(y) + "_evlevel_z"+str(zone)+".csv"
                level_zone = pd.read_csv(results_path/level_fn)
                level_zone.index = pd.to_datetime(level_zone.index)
                level_zone.to_excel(writer, sheet_name=str(zone), index=True)
        reserve_fn_xlsx = "1_"+scen_name + "_ev_reserve_allz"+str(y)+".xlsx"
        with pd.ExcelWriter(results_path/reserve_fn_xlsx) as writer:
            for zone in zonelist:
                reserve_fn = scen_name + str(y) + "_evreserve_z"+str(zone)+".csv"
                reserve_zone = pd.read_csv(results_path/reserve_fn)
                reserve_zone.index = pd.to_datetime(reserve_zone.index)
                reserve_zone.to_excel(writer, sheet_name=str(zone),index=True)
        v2g_fn_xlsx = "1_"+scen_name + "_ev_v2g_allz"+str(y)+".xlsx"
        with pd.ExcelWriter(results_path/v2g_fn_xlsx) as writer:
            for zone in zonelist:
                v2g_fn = scen_name + str(y) + "_v2g_z"+str(zone)+".csv"
                v2g_zone = pd.read_csv(results_path/v2g_fn)
                v2g_zone.index = pd.to_datetime(v2g_zone.index)
                v2g_zone.to_excel(writer, sheet_name=str(zone),index=True)

    return

# Consolidate traces (demand) to have all regions in same tab, years in separate tabs (in same workbook)
def consolidateDemandTraces(scen_name):
    results_path = Path(base_path/scen_name/"results")
    output_path = Path(base_path/scen_name)
    master_results_file = pd.DataFrame()

    master_results_fn_xlsx = "1"+scen_name + "_demand_all_years.xlsx"
    with pd.ExcelWriter(output_path/master_results_fn_xlsx) as writer:
        for y in yearlist:
            # Consolidate all regions (separate files) into same df
            yearly_results_file = pd.DataFrame()
            for reg in regionlist:
                filename = scen_name + str(y) + "_demand_region_"+str(reg)+".csv"
                try:
                    reg_results = pd.read_csv(results_path/filename, index_col=0)
                    # print(reg_results)
                except FileNotFoundError:
                    print("--- scen: {} for {} not found - skipping".format(scen_name,y))
                    continue
                reg_results.index = pd.to_datetime(reg_results.index)
                reg_results.columns = [reg]

                if reg == regionlist[0]:
                    yearly_results_file = reg_results.copy()
                else:  # Merge with master
                    yearly_results_file = pd.merge(yearly_results_file, reg_results, how='outer', left_index=True, right_index=True)
                # print(yearly_results_file)

            # Export this year to single tab
            yearly_results_file.to_excel(writer, sheet_name=str(y), index=True)

    return

# Consolidate traces (per zone) to have zones in separate tabs (in same workbook - and have one per year)
def consolidateZoneTraces(scen_name):
    # Consolidate all zones for generation & storage traces to single workbook
    results_path = Path(base_path/scen_name/"results")
    output_path = Path(base_path/scen_name)
    for y in yearlist:
        # Generation traces -> all zones consolidated into yearly xlsx file
        gen_fn_xlsx = "1_"+scen_name + "_generation_allz"+str(y)+".xlsx"
        with pd.ExcelWriter(results_path/gen_fn_xlsx) as writer:
            for zone in zonelist:
                gen_fn = scen_name + str(y) + "_generation_z"+str(zone)+".csv"
                gen_zone = pd.read_csv(results_path/gen_fn)
                gen_zone.index = pd.to_datetime(gen_zone.index)
                gen_zone.to_excel(writer, sheet_name=str(zone), index=True)
        stor_fn_xlsx = "1_"+scen_name + "_stor_charge_allz"+str(y)+".xlsx"
        with pd.ExcelWriter(results_path/stor_fn_xlsx) as writer:
            for zone in zonelist:
                stor_fn = scen_name + str(y) + "_stor_charge_load_z"+str(zone)+".csv"
                stor_charge_zone = pd.read_csv(results_path/stor_fn)
                stor_charge_zone.index = pd.to_datetime(stor_charge_zone.index)
                stor_charge_zone.to_excel(writer, sheet_name=str(zone), index=True)

    # Consolidate all years for interconn flows into single workbook
    master_results_file = pd.DataFrame()
    intercon_fn_xlsx = "1_"+scen_name + "_interconnection_flows_all_years.xlsx"
    with pd.ExcelWriter(output_path/intercon_fn_xlsx) as writer:
        for y in yearlist:
            filename = scen_name + str(y)+"_interconnector_flows.csv"
            year_results = pd.read_csv(results_path/filename,index_col=0)
            year_results.index = pd.to_datetime(year_results.index)
            year_results.to_excel(writer, sheet_name=str(y), index=True)

    #"1_"+out + "_"+ str(yearyear)+ "_transmission_capacity.csv"
    # "1_"+out + "_"+ str(yearyear)+ "_generation_capacity_per_zone.xlsx"
    return

for scen in scen_list:
    print(scen)
    consolidateResults(scen)
    consolidateEVTraces(scen)
    consolidateDemandTraces(scen)
    consolidateZoneTraces(scen)
