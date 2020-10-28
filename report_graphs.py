## Consolidate the traces & results output by opencem inot more useable forms

## Command to run all scenarios one after another
# python msolve.py test_bau.cfg -t --solver=gurobi & python msolve.py test_evs_dumb.cfg -t --solver=gurobi & python msolve.py test_bau_aemo_evs_load.cfg -t --solver=gurobi & python msolve.py test_evs_smart_0fit.cfg -t --solver=gurobi & python msolve.py test_evs_smart_25fit.cfg -t --solver=gurobi & python msolve.py test_evs_smart_50fit.cfg -t --solver=gurobi & python msolve.py test_evs_smart_100fit.cfg -t --solver=gurobi & python msolve.py test_evs_smart_200fit.cfg -t --solver=gurobi  & python msolve.py test_evs_smart_reward_50.cfg -t --solver=gurobi & python msolve.py test_evs_smart_reward_100.cfg -t --solver=gurobi & python msolve.py test_evs_smart_reward_200.cfg -t --solver=gurobi & python msolve.py test_evs_smart_reward_500.cfg -t --solver=gurobi & python msolve.py test_evs_v2g_0fit.cfg -t --solver=gurobi & python msolve.py test_evs_v2g_25fit.cfg -t --solver=gurobi & python msolve.py test_evs_v2g_50fit.cfg -t --solver=gurobi & python msolve.py test_evs_v2g_100fit.cfg -t --solver=gurobi & python msolve.py test_evs_v2g_200fit.cfg -t --solver=gurobi & python report_graphs.py



# & python msolve.py 1_test_evs_dumb.cfg -t --solver=gurobi & python msolve.py 1_test_evs_smart_0fit.cfg -t --solver=gurobi & python msolve.py 1_test_evs_smart_100fit.cfg -t --solver=gurobi & python msolve.py 1_test_evs_smart_reward_100.cfg -t --solver=gurobi & python msolve.py 1_test_evs_smart_reward_500.cfg -t --solver=gurobi & python msolve.py 1_test_evs_v2g_0fit.cfg -t --solver=gurobi & python msolve.py 1_test_evs_v2g_100fit.cfg -t --solver=gurobi & python msolve.py 1_test_bau_aemo_evs_load.cfg -t --solver=gurobi & python msolve.py 1_test_evs_smart_25fit.cfg -t --solver=gurobi & python msolve.py 1_test_evs_smart_50fit.cfg -t --solver=gurobi & python msolve.py 1_test_evs_smart_200fit.cfg -t --solver=gurobi  & python msolve.py 1_test_evs_smart_reward_50.cfg -t --solver=gurobi & python msolve.py 1_test_evs_smart_reward_200.cfg -t --solver=gurobi & python msolve.py 1_test_evs_v2g_25fit.cfg -t --solver=gurobi & python msolve.py 1_test_evs_v2g_50fit.cfg -t --solver=gurobi & python msolve.py 1_test_evs_v2g_200fit.cfg -t --solver=gurobi & python report_graphs.py

# python msolve.py 1_test_bau.cfg -t --solver=gurobi





# Import modules
from pathlib import Path
import pandas as pd
import os
import datetime as dt

#Name constants
scen_list = ["1_test_evs_v2g_100fit"] # =["test_bau","test_evs_dumb","test_bau_aemo_evs_load","test_evs_smart_0fit","test_evs_smart_25fit","test_evs_smart_50fit","test_evs_smart_100fit","test_evs_smart_200fit","test_evs_smart_reward_50","test_evs_smart_reward_100","test_evs_smart_reward_200","test_evs_smart_reward_500","test_evs_v2g_0fit","test_evs_v2g_25fit","test_evs_v2g_50fit","test_evs_v2g_100fit","test_evs_v2g_200fit"] #
yearlist = ["2021","2026","2031","2036","2041","2046","2050"]
zonelist = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
regionlist = [1,2,3,4,5]
base_path = Path("E:/OneDrive - UNSW/PhD/Modelling/openCEMKP/scenarios/")
zones_regions_dict = {5:1,6:1,7:1,8:1,1:2,2:2,3:2,4:2,9:5,10:5,11:5,12:5,13:3,14:3,15:3,16:4}


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

            # Add daytype & hour columns
            year_results["Day"] = year_results.index.dayofweek
            year_results["Hour"] = year_results.index.hour

            # Export yearly tab
            year_results.to_excel(writer, sheet_name=str(y), index=True)

            # Aggregated Flow Workbook (Into Zones)
            net_into_zones_yearly = pd.DataFrame()
            for z in zonelist:
                string_in = "d"+str(z)+"\Z"
                string_out = "z"+str(z)+"_"
                # print("Net flows into z{}, in:{}, out: {}".format(z,string_in,string_out))
                #Find columns that include strs above
                df_into = year_results.filter(regex=string_in)
                df_outof = year_results.filter(regex=string_out)
                df_outof = df_outof*(-1)
                # print(df_into)
                # print(df_outof)
                df_zone_flow = pd.merge(df_into, df_outof, how='outer', left_index=True, right_index=True)
                df_zone_flow["Sum"] = df_zone_flow.sum(axis=1)
                # print(df_zone_flow)

                # Gather the 2050 column and merge
                col_z_flow = df_zone_flow[["Sum"]]
                # col_z_flow = df_zone_flow["Sum"] #scen_results.copy().drop(["2021","2026","2031","2036","2041","2046"],axis=1)
                col_z_flow.rename(columns= {"Sum": str(z)}, inplace = True)

                if z == 1:
                    # print("First scenario")
                    net_into_zones_yearly = col_z_flow.copy()
                    # print(net_into_zones_yearly)
                else:
                    net_into_zones_yearly = pd.merge(net_into_zones_yearly, col_z_flow, how='outer', left_index=True, right_index=True)
                    # print(net_into_zones_yearly)
            sn_sum = "Net_z_" + str(y)
            net_into_zones_yearly.to_excel(writer, sheet_name=sn_sum, index=True)

            # Consolidate new tab for each year to show average flows per hour (weekday & weekend) into each zone and aggregated to into each region
            print(year_results)
            weekday = year_results.loc[year_results["Day"]<5]
            weekend = year_results.loc[year_results["Day"]>=5]
            print(weekend)
            hourly_ave_weekday = weekday.groupby([weekday.index.hour]).mean()
            hourly_ave_weekend = weekend.groupby([weekend.index.hour]).mean()
            print(hourly_ave_weekend)
            # df.groupby([df["Date/Time"].dt.year, df["Date/Time"].dt.hour]).mean()
            # hourly_ave_weekday = weekday.resample('H').mean()
            # hourly_ave_weekend = weekend.resample('H').mean()
            sn_wd = "Ave WD "+str(y)
            sn_we = "Ave WE "+str(y)
            hourly_ave_weekday.to_excel(writer, sheet_name=sn_wd, index=True)
            hourly_ave_weekend.to_excel(writer, sheet_name=sn_we, index=True)


    return

# Consolidate capacity results to be single sheet -> years columns, merge to have same rows
def consolidateCapacityResults(scen_name):
    results_path = Path(base_path/scen_name/"results")
    output_path = Path(base_path/scen_name)

    # Transmission & Interconnector Capacity
    master_results_file = pd.DataFrame()
    for y in yearlist:
        filename = "1_"+scen_name + "_" +str(y)+ "_transmission_capacity.csv"
        try:
            year_results = pd.read_csv(results_path/filename)
        except FileNotFoundError:
            print("--- scen: {} for {} not found - skipping".format(scen_name,y))
            continue
        year_result_t = year_results.transpose()
        year_result_t.columns =[y]
        if y == yearlist[0]:
            master_results_file = year_result_t.copy()
        else:  # Merge with master
            master_results_file = pd.merge(master_results_file, year_result_t, how='outer', left_index=True, right_index=True)
    # Export
    fn_out = scen_name+"_intercon_cap_results.csv"
    master_results_file.to_csv(output_path/fn_out)

    # Generation Capacity -> sheets per year containing all zones
    gen_cap_fn_xlsx = scen_name + "_generation_cap_all_years.xlsx"
    with pd.ExcelWriter(output_path/gen_cap_fn_xlsx) as writer:
        yearly_sum_df = pd.DataFrame()
        counter = 0
        for y in yearlist:
            master_gen_results_file = pd.DataFrame()
            for z in zonelist:
                zone_results = pd.DataFrame()
                filename = "1_"+scen_name + "_" +str(y)+ "_generation_capacity_z"+str(z)+".csv"
                try:
                    zone_results = pd.read_csv(results_path/filename)
                except FileNotFoundError:
                    print("--- scen: {} for {} not found - skipping".format(scen_name,y))
                    continue
                # year_results.index = pd.to_datetime(year_results.index)
                zone_result_t = zone_results.transpose()
                zone_result_t.columns =[z]

                # print(zone_result_t)
                if z == zonelist[0]:
                    master_gen_results_file = zone_result_t.copy()
                else:  # Merge with master
                    master_gen_results_file = pd.merge(master_gen_results_file, zone_result_t, how='outer', left_index=True, right_index=True)
                # print(master_gen_results_file)
            # print(master_gen_results_file)
            master_gen_results_file["Total_All_Zones"] = master_gen_results_file.sum(axis=1)
            master_gen_results_file.to_excel(writer, sheet_name=str(y), index=True)

            # Create new tab with yearly totals (all zones)
            # Gather the 2050 column and merge
            col_yr_sum = master_gen_results_file.copy().drop([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],axis=1)
            col_yr_sum.rename(columns= {"Total_All_Zones": y}, inplace = True)

            if counter == 0:
                # print("First scenario")
                yearly_sum_df = col_yr_sum.copy()
            else:
                yearly_sum_df = pd.merge(yearly_sum_df, col_yr_sum, how='outer', left_index=True, right_index=True)

            counter = counter +1

        yearly_sum_df.to_excel(writer, sheet_name="Total_All_Years", index=True)

    return

def combineScenIntercons():
    inter_cap_fn_xlsx = "Intercon_cap_all_scens.xlsx"
    df_2050 = pd.DataFrame()
    with pd.ExcelWriter(base_path/inter_cap_fn_xlsx) as writer:
        counter = 0
        for scen in scen_list:
            # print("\n ************************{}******************** ".format(scen))
            input_path = Path(base_path/scen)
            fn = scen + "_intercon_cap_results.csv"
            try:
                scen_results = pd.read_csv(input_path/fn, index_col=0, header=0)

                # if len(scen_results)==0:
                #     print("Empty db")
                #     continue
                if "2050" not in scen_results.columns:
                    print("Empty db / no 2050 column")
                    continue

                # Add difference column
                scen_results = scen_results.div(1000)#/1000
                scen_results = scen_results.fillna(0)#, inplace=True)
                scen_results["Increase_2050_2021"] = scen_results["2050"] - scen_results["2021"]

                betweenTwoDifferentSymbols = scen_results.index.str.split('_z').str[1]
                zs=betweenTwoDifferentSymbols.str.split('_d').str[0]
                # print(btds)
                scen_results["Zone_Source"] = pd.to_numeric(zs) #zs.astype(int)
                # print(scen_results["Zone_Source"])
                zd=scen_results.index.str.split('_d').str[1]
                scen_results["Zone_Dest"] = pd.to_numeric(zd) #zd.astype(int)
                scen_results["Region_Source"] = scen_results["Zone_Source"].map(zones_regions_dict)
                scen_results["Region_Dest"] = scen_results["Zone_Dest"].map(zones_regions_dict)
                scen_results.loc['Total',:]= scen_results.sum(axis=0)
                # print(scen_results)

                scen_results.to_excel(writer, sheet_name=str(scen), index=True)

                # Gather the 2050 column and merge
                col_2050 = scen_results.copy().drop(["2021","2026","2031","2036","2041","2046","Increase_2050_2021","Zone_Source","Zone_Dest","Region_Source","Region_Dest"],axis=1)
                col_2050.rename(columns= {"2050": scen}, inplace = True)

                col_abs_incr = scen_results.copy().drop(["2021","2026","2031","2036","2041","2046","2050","Zone_Source","Zone_Dest","Region_Source","Region_Dest"],axis=1)
                col_abs_incr.rename(columns= {"Increase_2050_2021": scen}, inplace = True)

                if counter == 0:
                    # print("First scenario")
                    df_2050 = col_2050.copy()
                    df_abs_increases = col_abs_incr.copy()
                else:
                    df_2050 = pd.merge(df_2050, col_2050, how='outer', left_index=True, right_index=True)
                    df_abs_increases = pd.merge(df_abs_increases, col_abs_incr, how='outer', left_index=True, right_index=True)
                # print(df_2050)
                counter = counter + 1

            except FileNotFoundError:
                print("--- intercon summary for scen: {} not found - skipping".format(scen))
                continue

        betweenTwoDifferentSymbols = df_2050.index.str.split('_z').str[1]
        zs=betweenTwoDifferentSymbols.str.split('_d').str[0]
        # print(btds)
        df_2050["Zone_Source"] = pd.to_numeric(zs) #zs.astype(int)
        # print(scen_results["Zone_Source"])
        zd=df_2050.index.str.split('_d').str[1]
        df_2050["Zone_Dest"] = pd.to_numeric(zd) #zd.astype(int)
        df_2050["Region_Source"] = df_2050["Zone_Source"].map(zones_regions_dict)
        df_2050["Region_Dest"] = df_2050["Zone_Dest"].map(zones_regions_dict)

        betweenTwoDifferentSymbols2 = df_abs_increases.index.str.split('_z').str[1]
        zs2=betweenTwoDifferentSymbols2.str.split('_d').str[0]
        # print(btds)
        df_abs_increases["Zone_Source"] = pd.to_numeric(zs2) #zs.astype(int)
        # print(scen_results["Zone_Source"])
        zd2=df_abs_increases.index.str.split('_d').str[1]
        df_abs_increases["Zone_Dest"] = pd.to_numeric(zd2) #zd.astype(int)
        df_abs_increases["Region_Source"] = df_abs_increases["Zone_Source"].map(zones_regions_dict)
        df_abs_increases["Region_Dest"] = df_abs_increases["Zone_Dest"].map(zones_regions_dict)

        df_2050.to_excel(writer, sheet_name="2050_Comp", index=True)
        df_abs_increases.to_excel(writer, sheet_name="Abs_Increases", index=True)
    return

def combineScenResults():
    results_fn_xlsx = "Basic_Results_all_scens.xlsx"
    df_2050 = pd.DataFrame()
    with pd.ExcelWriter(base_path/results_fn_xlsx, options={'strings_to_numbers': True}) as writer:
        counter = 0
        for scen in scen_list:
            # print("\n ************************{}******************** ".format(scen))
            input_path = Path(base_path/scen)
            fn = scen + "_results.csv"
            try:
                scen_results = pd.read_csv(input_path/fn, index_col=0, header=0)

                if "2050" not in scen_results.columns:
                    print("Empty db / no 2050 column")
                    continue

                # Add difference column
                # scen_results = scen_results
                # scen_results = scen_results.fillna(0)#, inplace=True)
                # scen_results["Increase_2050_2021"] = scen_results["2050"] - scen_results["2021"]
                scen_results.to_excel(writer, sheet_name=str(scen), index=True)

                # Gather the 2050 column and merge
                col_2050 = scen_results.copy().drop(["2021","2026","2031","2036","2041","2046"],axis=1)
                col_2050.rename(columns= {"2050": scen}, inplace = True)

                if counter == 0:
                    # print("First scenario")
                    df_2050 = col_2050.copy()
                else:
                    df_2050 = pd.merge(df_2050, col_2050, how='outer', left_index=True, right_index=True)
                # print(df_2050)
                counter = counter + 1

            except FileNotFoundError:
                print("--- results summary for scen: {} not found - skipping".format(scen))
                continue

        df_2050.to_excel(writer, sheet_name="2050_Comp", index=True)
    return


for scen in scen_list:
    print(scen)
    consolidateResults(scen)
    consolidateEVTraces(scen)
    consolidateDemandTraces(scen)
    consolidateZoneTraces(scen)
    consolidateCapacityResults(scen)
# combineScenIntercons()
# combineScenResults()
