""" Utility scripts for openCEM"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"

import locale
import sys

import matplotlib.pyplot as plt
import numpy as np
from pyomo.environ import value
from si_prefix import si_format
import pandas as pd
from pathlib import Path

import cemo.const
import cemo.rules

results_dir = "E:/OneDrive - UNSW/PhD/Modelling/openCEMKP/scenarios/" #KP_MODIFIED

# Settings & Definitions
def printonly(instance, key):  # pragma: no cover
    '''pprint specified instance variable and exit'''
    if key == "all":
        instance.pprint()  # pprint whole instance
    else:
        try:
            instance.component(key).pprint()  # pprint for provided key
        except KeyError:
            print("openCEM solve.py (printonly): Model key '%s' does not exist in model"
                  % key)
            sys.exit(1)
def _get_textid(table):
    '''Return text label for technology from const module'''
    switch = {
        'technology_type': cemo.const.TECH_TYPE,
        'region': cemo.const.REGION
    }
    return switch.get(table, lambda: "Name list not found")
def _techsinregion(instance, region):  # pragma: no cover
    techsinregion = set()
    # Populate with intersecton of .gen_tech_per_zone set for all zones in region
    for z in instance.zones_per_region[region]:
        techsinregion = techsinregion | instance.gen_tech_per_zone[z]()
        techsinregion = techsinregion | instance.hyb_tech_per_zone[z]()
        techsinregion = techsinregion | instance.stor_tech_per_zone[z]()
    return sorted(techsinregion, key=cemo.const.DISPLAY_ORDER.index)
def _evsinregion(instance, region): #KP_MODIFIED_070920
    evsinregion = set()
    # Populate with intersecton of .gen_tech_per_zone set for all zones in region
    for z in instance.zones_per_region[region]:
        evsinregion = evsinregion | instance.ev_tech_per_zone[z]() #KP_MODIFIED_180820
    return sorted(evsinregion, key=cemo.const.DISPLAY_ORDER.index)
def palette(instance, techsinregion):  # pragma: no cover
    '''Return a palette of tech colours for the set of techs in region given'''
    pal = cemo.const.PALETTE
    return [pal[k] for k in techsinregion]

# Save results to csv files
def save_results(inst, out,yearyear): #KP_MODIFIED - this section is from Dan
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    hours = float(len(inst.t))
    techtotal = [0] * len(inst.all_tech)
    evtechtotal = [0] * len(inst.all_tech)
    disptotal = [0] * len(inst.all_tech)
    evdisptotal = [0] * len(inst.all_tech)
    capftotal = [0] * len(inst.all_tech)
    nperz = [0] * len(inst.all_tech)
    idx = list(inst.all_tech)
    for z in inst.zones:
        for n in inst.gen_tech_per_zone[z]:
            techtotal[idx.index(n)] += value(inst.gen_cap_op[z, n])
            disptotal[idx.index(n)] += value(sum(inst.gen_disp[z, n, t]
                                                 for t in inst.t))
            capftotal[idx.index(n)] += value(sum(inst.gen_cap_factor[z, n, t]
                                                 for t in inst.t))
            nperz[idx.index(n)] += 1
        for s in inst.stor_tech_per_zone[z]:
            techtotal[idx.index(s)] += value(inst.stor_cap_op[z, s])
            disptotal[idx.index(s)] += value(sum(inst.stor_disp[z, s, t]
                                                 for t in inst.t))
            capftotal[idx.index(s)] += 0.5 * hours
            nperz[idx.index(s)] += 1
        for e in inst.ev_tech_per_zone[z]:
            techtotal[idx.index(e)] += value(inst.ev_cap_op[z, e])
            evtechtotal[idx.index(e)] += value(inst.ev_cap_op[z, e])
            disptotal[idx.index(e)] += value(sum(inst.ev_v2g_disp[z, e, t]
                                                 for t in inst.t))
            evdisptotal[idx.index(e)] += value(sum(inst.ev_v2g_disp[z, e, t]
                                                 for t in inst.t))
            capftotal[idx.index(e)] += 0.5 * hours
            nperz[idx.index(e)] += 1
        for h in inst.hyb_tech_per_zone[z]:
            techtotal[idx.index(h)] += value(inst.hyb_cap_op[z, h])
            disptotal[idx.index(h)] += value(sum(inst.hyb_disp[z, h, t]
                                                 for t in inst.t))
            capftotal[idx.index(h)] += value(sum(inst.hyb_cap_factor[z, h, t]
                                                 for t in inst.t))
            nperz[idx.index(h)] += 1

    df = pd.DataFrame()
    df['1_NEM_Capacity_Total'] = [sum(techtotal)]
    df['1_NEM_EV_Capacity_Total'] = [sum(evtechtotal)]
    # df['1_NEM_Capacity_Gens'] = [sum(techtotal)] - [sum(evtechtotal)]
    df['1_NEM_Dispatch_Total'] = [sum(disptotal)]
    df['1_NEM_EV_Dispatch_Total'] = [sum(evdisptotal)]
    # df['1_NEM_Dispatch_Gens'] = [sum(disptotal)] - [sum(evdisptotal)]

    for r in inst.regions:
        load = sum(inst.region_net_demand_less_evs[r, t] for t in inst.t) #(np.array([value(inst.region_net_demand_less_evs[r, t]) for t in inst.t]))
        # load_less_evs = sum(inst.region_net_demand_less_evs[r, t] for t in inst.t) #KP_MODIFIED_170820
        # aemo_ev_load = sum(inst.aemo_ev[r, t] for t in inst.t) #KP_MODIFIED_170820
        # df['Total Load'] = [sum(load)/1000]
        df['Load_'+str(rname[r])] = [load] #[sum(load)/1000]
        # df['Load_less_evs'+str(rname[r])] = [load_less_evs] #KP_MODIFIED_170820
        # df['Load_aemo_ev'+str(rname[r])] = [aemo_ev_load] #KP_MODIFIED_170820

    for j in inst.all_tech:
        if techtotal[idx.index(j)] > 0:
            df['2_Cap_'+str(tname[j])] = [techtotal[idx.index(j)] * 1e6]
            df['3_Dis_'+str(tname[j])] = [disptotal[idx.index(j)] * 1e6]
            df['4_Ave_cf_'+str(tname[j])] = [disptotal[idx.index(j)] / hours / techtotal[idx.index(j)]* 1e3]

    # df['Total Cost'] = [locale.currency(value(inst.Obj - cemo.rules.cost_shadow(inst)))]

    df['5_System_Cost'] = [locale.currency(value(cemo.rules.system_cost(inst)))]
    df['5_Obj_Cost'] = [locale.currency(value(cemo.rules.obj_cost(inst)))]
    df['5_Shadow Costs'] = [locale.currency(value(cemo.rules.cost_shadow(inst)))]
    #df['Dan Obj Less Shadow'] = [locale.currency(value(inst.Obj - cemo.rules.cost_shadow(inst)))]

    df["6_LCOE"] = [locale.currency(value((inst.Obj - cemo.rules.cost_shadow(inst)) / sum(inst.region_net_demand_less_evs[r, t]
                                                                                for r in inst.regions
                                                                                for t in inst.t)))]
    df["5_Build_Cost"] = [locale.currency(value(cemo.rules.cost_capital(inst)))]
    # df["7_Build_cost_endo"]=[locale.currency(sum(value(cemo.rules.cost_build_per_zone_model(inst, zone) for zone in inst.zones)))]
    # df["7_Build_cost_exo"]=[locale.currency(sum(value(cemo.rules.cost_build_per_zone_exo(inst, zone) for zone in inst.zones)))]

    df["5_Repayment_cost"]=[locale.currency(value(sum(inst.cost_cap_carry_forward[z] for z in inst.zones)))]
    df["5_Operating_cost"] =[locale.currency(value(cemo.rules.cost_operating(inst)))]
    df["5_Fixed_cost"] =[locale.currency(value(cemo.rules.cost_fixed(inst)))]
    df["5_Trans_build_cost"]= [locale.currency(value(cemo.rules.cost_trans_build(inst)))]

    # df["7_Trans_build_cost_endo"]=[locale.currency(sum(value(cemo.rules.cost_trans_build_per_zone_model(inst, zone)) for zone in inst.zones))]
    # df["7_Trans_build_cost_exo"]=[locale.currency(sum(value(cemo.rules.cost_trans_build_per_zone_exo(inst, zone)) for zone in inst.zones))]
    df["5_Trans_flow_cost"]=[locale.currency(value(cemo.rules.cost_trans_flow(inst)))]
    df["5_Unserved_cost"]=[locale.currency(value(cemo.rules.cost_unserved(inst)))]

    df["5_Emission_cost"]=[locale.currency(value(cemo.rules.cost_emissions(inst)))]
    df["5_Retirmt_cost"]=[locale.currency(value(cemo.rules.cost_retirement(inst)))]

    df["5_V2G_Payments"] = [locale.currency(value(cemo.rules.cost_v2g_payments(inst)))]
    df["5_Smart_Payments"] = [locale.currency(value(cemo.rules.cost_smart_payments(inst)))]

    total_emissions = 0
    total_dispatch = 0
    for r in inst.regions:
        total_emissions = total_emissions + value(cemo.rules.emissions(inst, r))
        total_dispatch = total_dispatch + value(cemo.rules.dispatch(inst, r))
        # df["8_Emissions_NEM"]=total_emissions
        # df['2_Cap_'+str(tname[j])] = [techtotal[idx.index(j)] * 1e6]
    emrate = total_emissions/(total_dispatch+ 1.0e-12) # so its not dividing by 0
    df["8_Emissions_rate_kgMWh"]=[emrate]
    df["8_Emissions_NEM"]=total_emissions

    df.to_csv(results_dir + out  +'/results/' +out+'_results_'+str(yearyear)+'.csv')
def save_ev_results(inst, out,yearyear): #KP_MODIFIED - this section is from Dan
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    hours = float(len(inst.t))
    techtotal = [0] * len(inst.all_tech)
    v2gtotal = [0] * len(inst.all_tech)
    smarttotal = [0] * len(inst.all_tech)
    dumbtotal = [0] * len(inst.all_tech)
    chargetotal = [0] * len(inst.all_tech)
    transtotal = [0] * len(inst.all_tech)
    numvehtotal = [0] * len(inst.all_tech)
    numsmartvehtotal = [0] * len(inst.all_tech)
    nperz = [0] * len(inst.all_tech)
    idx = list(inst.all_tech)
    for z in inst.zones:
        for e in inst.ev_tech_per_zone[z]:
            techtotal[idx.index(e)] += value(inst.ev_cap_op[z, e])
            v2gtotal[idx.index(e)] += value(sum(inst.ev_v2g_disp[z, e, t]
                                                 for t in inst.t))
            smarttotal[idx.index(e)] += value(sum(inst.ev_smart_charge[z, e, t]
                                                 for t in inst.t))
            dumbtotal[idx.index(e)] += value(sum(inst.ev_dumb_charge[z, e, t]
                                                 for t in inst.t))
            chargetotal[idx.index(e)] += value(sum(inst.ev_charge[z, e, t]
                                                 for t in inst.t))
            transtotal[idx.index(e)] += value(sum(inst.ev_disp_transport[z, e, t]
                                                 for t in inst.t))
            numvehtotal[idx.index(e)] += value(inst.ev_num_vehs[z,e])
            numsmartvehtotal[idx.index(e)] += value(inst.ev_num_smart_part[z,e])
            nperz[idx.index(e)] += 1

    df = pd.DataFrame()
    for j in inst.all_tech:
        if techtotal[idx.index(j)] > 0:
            df['MWh_'+str(tname[j])] = [techtotal[idx.index(j)]]
            df['V2G_'+str(tname[j])] = [v2gtotal[idx.index(j)]]
            df['Smart_MWh_'+str(tname[j])] = [smarttotal[idx.index(j)]]
            df['Dumb_MWh_'+str(tname[j])] = [dumbtotal[idx.index(j)]]
            df['Charge_MWh_'+str(tname[j])] = [chargetotal[idx.index(j)]]
            df['Trans_MWh_'+str(tname[j])] = [transtotal[idx.index(j)]]
            df['Num_Veh_'+str(tname[j])] = [numvehtotal[idx.index(j)]]
            df['Num_Veh_Smart_Part'+str(tname[j])] = [numsmartvehtotal[idx.index(j)]]
            # df['Num_Veh_'+str(tname[j])] = [numvehtotal[idx.index(j)]]
            # df['avg cap factor'+str(tname[j])] = [disptotal[idx.index(j)] / hours / techtotal[idx.index(j)]* 1e3]

            df['Smart_FiT_$MWh_'+str(tname[j])] = value(inst.cost_ev_smart_vom[j])
            df['V2G_FiT_$MWh_'+str(tname[j])] = value(inst.cost_ev_vom[j])

    df["V2G Payments $"] = [locale.currency(value(cemo.rules.cost_v2g_payments(inst)))]
    df["Smart Payments $"] = [locale.currency(value(cemo.rules.cost_smart_payments(inst)))]

    df.to_csv(results_dir + out  +'/results/' +out+'_ev_results_'+str(yearyear)+'.csv')
# def save_ev_disp_sum_zone(inst, out,yearyear):
#     tname = _get_textid('technology_type')
#     rname = _get_textid('region')
#     evtechtotal = [0] * len(inst.all_tech)
#     # techtotal = [0] * len(inst.all_tech)
#     nperz = [0] * len(inst.all_tech)
#     idx = list(inst.all_tech)
#
#     # Create separate xlsx tab per zone with capacity/technology as columns
#     for z in inst.zones:
#         df = pd.DataFrame() # dataframe per zone
#         for j in inst.all_tech:
#             for e in inst.ev_tech_per_zone[z]:
#                 evtechtotal[idx.index(e)] = value(inst.ev_cap_op[z, e])
#                 # df['Capcity_'+str(tname[j])] = value(inst.gen_cap_op[z, n]) #[techtotal[idx.index(j)] * 1e6]
#                 nperz[idx.index(e)] += 1
#         for j in inst.all_tech:
#             if evtechtotal[idx.index(j)] > 0:
#                 df['Capcity_'+str(tname[j])] = [evtechtotal[idx.index(j)] * 1e6]
#
#         df.to_csv(results_dir + out  +'/results/' + "1_"+out + "_"+ str(yearyear)+ "_ev_capacity_z"+str(z)+".csv")
#
#     return

def save_cap_zone_results(inst, out,yearyear):
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # techtotal = [0] * len(inst.all_tech)
    nperz = [0] * len(inst.all_tech)
    idx = list(inst.all_tech)

    # Create separate xlsx tab per zone with capacity/technology as columns
    gen_fn_xlsx = "1_"+out + "_"+ str(yearyear)+ "_generation_capacity_per_zone.xlsx"
    for z in inst.zones:
        df = pd.DataFrame() # dataframe per zone
        techtotal = [0] * len(inst.all_tech)
        for j in inst.all_tech:
            for n in inst.gen_tech_per_zone[z]:
                techtotal[idx.index(n)] = value(inst.gen_cap_op[z, n])
                # df['Capcity_'+str(tname[j])] = value(inst.gen_cap_op[z, n]) #[techtotal[idx.index(j)] * 1e6]
                nperz[idx.index(n)] += 1
            for s in inst.stor_tech_per_zone[z]:
                techtotal[idx.index(s)] = value(inst.stor_cap_op[z, s])
                # df['Capcity_'+str(tname[j])] = value(inst.stor_cap_op[z, s])
                nperz[idx.index(s)] += 1
            for h in inst.hyb_tech_per_zone[z]:
                techtotal[idx.index(h)] = value(inst.hyb_cap_op[z, h])
                # df['Capcity_'+str(tname[j])] = value(inst.hyb_cap_op[z, h])
                nperz[idx.index(h)] += 1
        # print(df)
        for j in inst.all_tech:
            if techtotal[idx.index(j)] > 0:
                df['Capcity_'+str(tname[j])] = [techtotal[idx.index(j)] * 1e6]

        df.to_csv(results_dir + out  +'/results/' + "1_"+out + "_"+ str(yearyear)+ "_generation_capacity_z"+str(z)+".csv")

    return
def save_intercon_cap_zone_results(inst, out,yearyear):
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    intercontotal = [0] * len(inst.intercons_in_zones)
    interconperz = [0] * len(inst.intercons_in_zones)
    idx = list(inst.intercons_in_zones)

    # Create separate xlsx tab per zone with capacity/technology as columns
    df2 = pd.DataFrame() # dataframe per zone
    for z in inst.zones:
        for dest in inst.intercon_per_zone[z]:
            name = "z"+str(z)+"_d"+str(dest)
            intercontotal[idx.index((z,dest))] = value(inst.intercon_cap_op[z, dest]) # intercon_cap_op[zone_source, zone_dest]
            interconperz[idx.index((z,dest))] += 1

        for dest in inst.intercon_per_zone[z]:
            if intercontotal[idx.index((z,dest))] > 0:
                name = "z"+str(z)+"_d"+str(dest)
                df2['Capcity_'+str(name)] = [intercontotal[idx.index((z,dest))] * 1e6]

    df2.to_csv(results_dir + out  +'/results/' + "1_"+out + "_"+ str(yearyear)+ "_transmission_capacity.csv")

    return
def save_ev_cap_zone_results(inst, out,yearyear):
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    evtechtotal = [0] * len(inst.all_tech)
    # techtotal = [0] * len(inst.all_tech)
    nperz = [0] * len(inst.all_tech)
    idx = list(inst.all_tech)

    # Create separate xlsx tab per zone with capacity/technology as columns
    for z in inst.zones:
        df = pd.DataFrame() # dataframe per zone
        for j in inst.all_tech:
            for e in inst.ev_tech_per_zone[z]:
                evtechtotal[idx.index(e)] = value(inst.ev_cap_op[z, e])
                # df['Capcity_'+str(tname[j])] = value(inst.gen_cap_op[z, n]) #[techtotal[idx.index(j)] * 1e6]
                nperz[idx.index(e)] += 1
        for j in inst.all_tech:
            if evtechtotal[idx.index(j)] > 0:
                df['Capcity_'+str(tname[j])] = [evtechtotal[idx.index(j)] * 1e6]

        df.to_csv(results_dir + out  +'/results/' + "1_"+out + "_"+ str(yearyear)+ "_ev_capacity_z"+str(z)+".csv")

    return
def save_ev_overall_results(instance, out,yearyear): # DOES NOT WORK FOR SOME UNKNOWN REASON
    # Export restuls per zone -> summary Table
    # Modes = columns, rows = sum transport, dumb charge, smart charge, total charge, v2g dispatch
    tname = _get_textid('technology_type')
    evtechtotal = [0] * len(instance.all_tech)
    evdisptotal = [0] * len(instance.all_tech)
    evdisptranstotal = [0] * len(instance.all_tech)
    evchargetotal = [0] * len(instance.all_tech)
    evdumbtotal = [0] * len(instance.all_tech)
    evsmarttotal = [0] * len(instance.all_tech)
    evnperz = [0] * len(instance.all_tech)
    idx = list(instance.all_tech)

    for z in instance.zones:
        rows = ["Capacity", "Transport_dispatch","Total_Charge","Dumb_Charge","Smart_Charge","V2G_dispatch"]
        df = pd.DataFrame(index = rows)

        for e in instance.ev_tech_per_zone[z]:
            # tech_name = tname[e]
            evtechtotal[idx.index(e)] = value(instance.ev_cap_op[z, e])
            evdisptotal[idx.index(e)] = value(sum(instance.ev_v2g_disp[z, e, t] for t in instance.t))
            evdisptranstotal[idx.index(e)] = value(sum(instance.ev_disp_transport[z, e, t] for t in instance.t))
            evchargetotal[idx.index(e)] = value(sum(instance.ev_charge[z, e, t] for t in instance.t))
            evdumbtotal[idx.index(e)] = value(sum(instance.ev_dumb_charge[z, e, t] for t in instance.t))
            evsmarttotal[idx.index(e)] = value(sum(instance.ev_smart_charge[z, e, t] for t in instance.t))

            df.loc["Capacity",e] = [evtechtotal[idx.index(e)] * 1e6]
            df.loc["Transport_dispatch",e] = [evdisptranstotal[idx.index(e)] * 1e6]
            df.loc["Total_Charge",e] = [evchargetotal[idx.index(e)] * 1e6]
            df.loc["Dumb_Charge",e] = [evdumbtotal[idx.index(e)] * 1e6]
            df.loc["Smart_Charge",e] = [evsmarttotal[idx.index(e)] * 1e6]
            df.loc["V2G_dispatch",e] = [evdisptotal[idx.index(e)] * 1e6]

            evnperz[idx.index(e)] += 1

        df.to_csv(results_dir + out  +'/results/' + "2_"+out + "_"+ str(yearyear)+ "_ev_sum_results_z"+str(z)+".csv")

    return
def save_ev_traces(instance,out,yearyear):
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    ts = np.array([t for t in instance.t], dtype=np.datetime64)

    for r in instance.regions:
        evsinregion = _evsinregion(instance, r)
        plabels = []
        for t in evsinregion:
            plabels.append(tname[t])
        pos = dict(zip(list(evsinregion), range(len(evsinregion))))

        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            transport_np = np.zeros([len(evsinregion), len(instance.t)])
            charge_np = np.zeros([len(evsinregion), len(instance.t)])
            dumbcharge_np = np.zeros([len(evsinregion), len(instance.t)])
            smartcharge_np = np.zeros([len(evsinregion), len(instance.t)])
            v2g_np = np.zeros([len(evsinregion), len(instance.t)])
            evlevel_np = np.zeros([len(evsinregion), len(instance.t)])
            evreserve_np = np.zeros([len(evsinregion), len(instance.t)])
            connected_np = np.zeros([len(evsinregion), len(instance.t)])
            for e in instance.ev_tech_per_zone[z]:
                transport_np[pos[e], :] = transport_np[pos[e], :] + \
                    np.array([value(instance.ev_disp_transport[z, e, t])
                              for t in instance.t])

                charge_np[pos[e], :] = charge_np[pos[e], :] + \
                    np.array([value(instance.ev_charge[z, e, t])
                              for t in instance.t])

                dumbcharge_np[pos[e], :] = dumbcharge_np[pos[e], :] + \
                    np.array([value(instance.ev_dumb_charge[z, e, t])
                              for t in instance.t])

                smartcharge_np[pos[e], :] = smartcharge_np[pos[e], :] + \
                    np.array([value(instance.ev_smart_charge[z, e, t])
                              for t in instance.t])

                v2g_np[pos[e], :] = v2g_np[pos[e], :] + \
                    np.array([value(instance.ev_v2g_disp[z, e, t])
                              for t in instance.t])

                evlevel_np[pos[e], :] = evlevel_np[pos[e], :] + \
                    np.array([value(instance.ev_level[z, e, t])
                              for t in instance.t])

                evreserve_np[pos[e], :] = evreserve_np[pos[e], :] + \
                    np.array([value(instance.ev_reserve[z, e, t])
                              for t in instance.t])

                connected_np[pos[e], :] = connected_np[pos[e], :] + \
                    np.array([value(instance.ev_connected[z, e, t])
                              for t in instance.t])

            transport_npdf = pd.DataFrame(transport_np)
            transport_npdf.columns = ts
            transport_npdf.index = plabels
            transport = transport_npdf.transpose()
            transport.to_csv(results_dir + out  +'/results/' + out +str(yearyear)+'_transport_z'+str(z)+'.csv', index = True)

            charge_npdf = pd.DataFrame(charge_np)
            charge_npdf.columns = ts
            charge_npdf.index = plabels
            charge = charge_npdf.transpose()
            charge.to_csv(results_dir + out  +'/results/' + out +str(yearyear)+'_charge_z'+str(z)+'.csv', index = True)

            dumbcharge_npdf = pd.DataFrame(dumbcharge_np)
            dumbcharge_npdf.columns = ts
            dumbcharge_npdf.index = plabels
            dumbcharge = dumbcharge_npdf.transpose()
            dumbcharge.to_csv(results_dir + out  +'/results/' + out +str(yearyear)+'_dumbcharge_z'+str(z)+'.csv', index = True)

            smartcharge_npdf = pd.DataFrame(smartcharge_np)
            smartcharge_npdf.columns = ts
            smartcharge_npdf.index = plabels
            smartcharge = smartcharge_npdf.transpose()
            smartcharge.to_csv(results_dir + out  +'/results/' + out +str(yearyear)+'_smartcharge_z'+str(z)+'.csv', index = True)

            v2g_npdf = pd.DataFrame(v2g_np)
            v2g_npdf.columns = ts
            v2g_npdf.index = plabels
            v2g = v2g_npdf.transpose()
            v2g.to_csv(results_dir + out  +'/results/' + out +str(yearyear)+'_v2g_z'+str(z)+'.csv', index = True)

            evlevel_npdf = pd.DataFrame(evlevel_np)
            evlevel_npdf.columns = ts
            evlevel_npdf.index = plabels
            evlevel = evlevel_npdf.transpose()
            evlevel.to_csv(results_dir + out  +'/results/' + out +str(yearyear)+'_evlevel_z'+str(z)+'.csv', index = True)

            evreserve_npdf = pd.DataFrame(evreserve_np)
            evreserve_npdf.columns = ts
            evreserve_npdf.index = plabels
            evreserve = evreserve_npdf.transpose()
            evreserve.to_csv(results_dir + out  +'/results/' + out +str(yearyear)+'_evreserve_z'+str(z)+'.csv', index = True)

            connected_npdf = pd.DataFrame(connected_np)
            connected_npdf.columns = ts
            connected_npdf.index = plabels
            connected = connected_npdf.transpose()
            connected.to_csv(results_dir + out  +'/results/' + out +str(yearyear)+'_evconnected_z'+str(z)+'.csv', index = True)
def save_gen_traces(instance,out,yearyear):
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    ts = np.array([t for t in instance.t], dtype=np.datetime64)

    for r in instance.regions:
        techsinregion = _techsinregion(instance, r)
        plabels = []
        for t in techsinregion:
            plabels.append(tname[t])
        pos = dict(zip(list(techsinregion), range(len(techsinregion))))

        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            gen_np = np.zeros([len(techsinregion), len(instance.t)])

            for n in instance.gen_tech_per_zone[z]:
                gen_np[pos[n], :] = gen_np[pos[n], :] + \
                    np.array([value(instance.gen_disp[z, n, t])
                              for t in instance.t])
            for s in instance.stor_tech_per_zone[z]:
                gen_np[pos[s], :] = gen_np[pos[s], :] + \
                    np.array([value(instance.stor_disp[z, s, t])
                              for t in instance.t])
            for h in instance.hyb_tech_per_zone[z]:
                gen_np[pos[h], :] = gen_np[pos[h], :] + \
                    np.array([value(instance.hyb_disp[z, h, t])
                              for t in instance.t])

            gen_npdf = pd.DataFrame(gen_np)
            gen_npdf.columns = ts
            gen_npdf.index = plabels
            gen = gen_npdf.transpose()
            gen.to_csv(results_dir + out  +'/results/' + out +str(yearyear)+'_generation_z'+str(z)+'.csv', index = True)
def save_intercon_traces(instance,out,yearyear):
    # tname = _get_textid('technology_type')
    # rname = _get_textid('region')
    ts = np.array([t for t in instance.t], dtype=np.datetime64)
    plabels =[]

    # Get label names and set up db
    for z in instance.zones:
        for dest in instance.intercon_per_zone[z]:
            name = "z"+str(z)+"_d"+str(dest)
            plabels.append(name)
            # print(name)
    # print(plabels)
    pos = dict(zip(list(plabels), range(len(plabels))))
    intercon_np = np.zeros([len(plabels), len(instance.t)])
    # print(intercon_np)

    # collect the total dispatch for each intercon link
    for z in instance.zones:
        for dest in instance.intercon_per_zone[z]:
            name = "z"+str(z)+"_d"+str(dest)
            # print(name)
            # print(np.array([value(instance.intercon_disp[z, dest, t]) for t in instance.t]))
            # intercon_np[name, :] = np.array([value(instance.intercon_disp[z, dest, t])) for t in instance.t])

            intercon_np[pos[name], :] = intercon_np[pos[name], :] + \
                np.array([value(instance.intercon_disp[z, dest, t])
                          for t in instance.t])

    # print(intercon_np)

    intercon_npdf = pd.DataFrame(intercon_np)
    intercon_npdf.columns = ts
    intercon_npdf.index = plabels
    intercon = intercon_npdf.transpose()
    intercon.to_csv(results_dir + out  +'/results/' + out +str(yearyear)+'_interconnector_flows.csv', index = True)
def save_load_traces(instance,out,yearyear):
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    ts = np.array([t for t in instance.t], dtype=np.datetime64)

    for r in instance.regions:
        techsinregion = _techsinregion(instance, r)
        plabels = []
        for t in techsinregion:
            plabels.append(tname[t])
        pos = dict(zip(list(techsinregion), range(len(techsinregion))))

        # gather load for NEM region from solved model instance
        load = np.array([value(instance.region_net_demand_less_evs[r, t])
                         for t in instance.t])
        demand_df = pd.DataFrame(load)
        demand_df.index = ts
        # demand = demand_df.transpose()
        demand_df.to_csv(results_dir + out  +'/results/' + out +str(yearyear)+'_demand_region_'+str(r)+'.csv', index = True)

        # collect the total charging load for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            load_np = np.zeros([len(techsinregion), len(instance.t)])

            for s in instance.stor_tech_per_zone[z]:
                load_np[pos[s], :] = load_np[pos[s], :] + \
                    np.array([value(instance.stor_charge[z, s, t])
                              for t in instance.t])

            load_npdf = pd.DataFrame(load_np)
            load_npdf.columns = ts
            load_npdf.index = plabels
            loads = load_npdf.transpose()
            loads.to_csv(results_dir + out  +'/results/' + out +str(yearyear)+'_stor_charge_load_z'+str(z)+'.csv', index = True)

# Plot results
def plotresults(instance, out,yearyear):  # pragma: no cover
    """ Process results to plot.
     Feel free to improve the efficiency of this code
    """
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # Process results to plot.
    # Feel free to improve the efficiency of this code
    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    ts = np.array([t for t in instance.t], dtype=np.datetime64)
    # cycle through NEM regions`
    for r in instance.regions:
        # Set of all technologies in a region
        techsinregion = _techsinregion(instance, r)
        # gather technology text_ids in region for plot labels
        plabels = []
        for t in techsinregion:
            plabels.append(tname[t])
        # append the label load
        plabels.insert(0, 'load')

        # gather load for NEM region from solved model instance
        load = np.array([value(instance.region_net_demand_less_evs[r, t])
                         for t in instance.t])
        # Empty array of dispatch qtt
        q_z_r = np.zeros([len(techsinregion), len(instance.t)])
        # positions of each tech in numpy array
        pos = dict(zip(list(techsinregion), range(len(techsinregion))))
        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            for n in instance.gen_tech_per_zone[z]:
                q_z_r[pos[n], :] = q_z_r[pos[n], :] + \
                    np.array([value(1e3 * instance.gen_disp[z, n, t])
                              for t in instance.t])
            for s in instance.stor_tech_per_zone[z]:
                q_z_r[pos[s], :] = q_z_r[pos[s], :] + \
                    np.array([value(1e3 * instance.stor_disp[z, s, t])
                              for t in instance.t])
            for h in instance.hyb_tech_per_zone[z]:
                q_z_r[pos[h], :] = q_z_r[pos[h], :] + \
                    np.array([value(1e3 * instance.hyb_disp[z, h, t])
                              for t in instance.t])
        # Plotting instructions
        # pick respective subplot
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        palr = palette(instance, techsinregion)
        ax.stackplot(ts, q_z_r, colors=palr)  # dispatch values
        ax.plot(ts, load, color='black')  # Put load on top
        ax.legend(plabels)  # put labels
        ax.set_title(rname[r])  # Region names

        fig.autofmt_xdate()
    # plt.show()
    plt.savefig(results_dir + out  +'/results/' + out  +'_dispatch_allgen_'+str(yearyear)+'.png')
def plotcapacity(instance, out,yearyear):  # pragma: no cover
    """ Stacked plot of capacities
     Feel free to improve the efficiency of this code
    """
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    # cycle through NEM regions`
    for r in instance.regions:
        # gather load for NEM region from solved model instance
        # empty set of all technologies in a region
        techsinregion = _techsinregion(instance, r)
        # gather technology text_ids in region for plot labels
        plabels = []
        for t in techsinregion:
            plabels.append(tname[t])

        # Empty array of gen_cap_op_r
        gen_cap_op_r = np.zeros([len(techsinregion)])
        gen_cap_new_r = np.zeros([len(techsinregion)])
        # positions of each tech in numpy array
        pos = dict(zip(list(techsinregion), range(len(techsinregion))))
        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            for n in instance.gen_tech_per_zone[z]:
                gen_cap_op_r[pos[n]] = gen_cap_op_r[pos[n]] + \
                    np.array([value(instance.gen_cap_op[z, n])])
                gen_cap_new_r[pos[n]] = gen_cap_new_r[pos[n]] + \
                    np.array([value(instance.gen_cap_new[z, n])])
            for s in instance.stor_tech_per_zone[z]:
                gen_cap_op_r[pos[s]] = gen_cap_op_r[pos[s]] + \
                    np.array([value(instance.stor_cap_op[z, s])])
                gen_cap_new_r[pos[s]] = gen_cap_new_r[pos[s]] + \
                    np.array([value(instance.stor_cap_new[z, s])])
            for h in instance.hyb_tech_per_zone[z]:
                gen_cap_op_r[pos[h]] = gen_cap_op_r[pos[h]] + \
                    np.array([value(instance.hyb_cap_op[z, h])])
                gen_cap_new_r[pos[h]] = gen_cap_new_r[pos[h]] + \
                    np.array([value(instance.hyb_cap_new[z, h])])

        N = np.arange(len(techsinregion))
        ExCap_r = gen_cap_op_r - gen_cap_new_r
        width = 0.35
        # Plotting instructions
        colour = palette(instance, techsinregion)
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        ax.bar(N, ExCap_r.tolist(), width, color=colour)  # Existing capacity
        ax.bar(N, gen_cap_new_r, width, bottom=ExCap_r,
               color=colour, edgecolor='white', hatch='////')  # New Capacity
        ax.set_xticks(N)
        ax.set_xticklabels([tname[t] for t in techsinregion])
        for tick in ax.get_xticklabels():
            tick.set_rotation(90)
        ax.set_title(rname[r], position=(0.9, 0.9))  # Region names
    # plt.show()
    plt.savefig(results_dir + out  +'/results/' + out  +'_capacity_allgen_'+str(yearyear)+'.png')
def plotevcapacity(instance,out,yearyear):
    """ Stacked plot of capacities
     Feel free to improve the efficiency of this code
    """
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    # cycle through NEM regions`
    for r in instance.regions:
        # gather load for NEM region from solved model instance
        # empty set of all technologies in a region
        evsinregion = _evsinregion(instance, r)
        # gather technology text_ids in region for plot labels
        plabels = []
        for t in evsinregion:
            plabels.append(tname[t])

        # Empty array of gen_cap_op_r
        gen_cap_op_r = np.zeros([len(evsinregion)])
        gen_cap_new_r = np.zeros([len(evsinregion)])
        # positions of each tech in numpy array
        pos = dict(zip(list(evsinregion), range(len(evsinregion))))
        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:

            for e in instance.ev_tech_per_zone[z]: #KP_ADDED
                gen_cap_op_r[pos[e]] = gen_cap_op_r[pos[e]] + \
                    np.array([value(instance.ev_cap_op[z, e])])


        N = np.arange(len(evsinregion))
        ExCap_r = gen_cap_op_r - gen_cap_new_r
        width = 0.35
        # Plotting instructions
        colour = palette(instance, evsinregion)
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        ax.bar(N, ExCap_r.tolist(), width, color=colour)  # Existing capacity
        ax.bar(N, gen_cap_new_r, width, bottom=ExCap_r,
               color=colour, edgecolor='white', hatch='////')  # New Capacity
        ax.set_xticks(N)
        ax.set_xticklabels([tname[t] for t in evsinregion])
        for tick in ax.get_xticklabels():
            tick.set_rotation(90)
        ax.set_title(rname[r], position=(0.9, 0.9))  # Region names
        # plt.legend(handles=[p1, p2], title='title', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='xx-small')
    # plt.show()
    plt.savefig(results_dir + out  +'/results/' + out  +'_ev_capacity_'+str(yearyear)+'.png')
def plot_evs(instance,scen_name,yearyear):
    tname = _get_textid('technology_type')
    for r in instance.regions:
        evsinregion = _evsinregion(instance, r)
        plabels = []
        for t in evsinregion:
            plabels.append(tname[t])
        # print(plabels)
    if len(plabels)>0:
        plotevcapacity(instance, scen_name, instance.name)
        plotevresults_v2g(instance, scen_name, instance.name)
        plotevresults_charge(instance, scen_name, instance.name)
        plotevresults_dumb_charge(instance, scen_name, instance.name)
        plotevresults_smart_charge(instance, scen_name, instance.name)
        plotevresults_transport(instance, scen_name, instance.name)
        save_ev_traces(instance, scen_name, instance.name)
    else:
        print("No EVS to print")
def plotevresults_v2g(instance,out,yearyear): #KP_MODIFIED_070920
    """ Process results to plot.
     Feel free to improve the efficiency of this code
    """
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # Process results to plot.
    # Feel free to improve the efficiency of this code
    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    ts = np.array([t for t in instance.t], dtype=np.datetime64)
    # cycle through NEM regions`
    for r in instance.regions:
        # Set of all technologies in a region
        evsinregion = _evsinregion(instance, r)
        # gather technology text_ids in region for plot labels
        plabels = []
        for t in techsinregion:
            plabels.append(tname[t])

        # Empty array of gen_cap_op_r
        gen_cap_op_r = np.zeros([len(techsinregion)])
        gen_cap_new_r = np.zeros([len(techsinregion)])
        # positions of each tech in numpy array
        pos = dict(zip(list(techsinregion), range(len(techsinregion))))
        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            for n in instance.gen_tech_per_zone[z]:
                gen_cap_op_r[pos[n]] = gen_cap_op_r[pos[n]] + \
                    np.array([value(instance.gen_cap_op[z, n])])
                gen_cap_new_r[pos[n]] = gen_cap_new_r[pos[n]] + \
                    np.array([value(instance.gen_cap_new[z, n])])
            for s in instance.stor_tech_per_zone[z]:
                gen_cap_op_r[pos[s]] = gen_cap_op_r[pos[s]] + \
                    np.array([value(instance.stor_cap_op[z, s])])
                gen_cap_new_r[pos[s]] = gen_cap_new_r[pos[s]] + \
                    np.array([value(instance.stor_cap_new[z, s])])
            for h in instance.hyb_tech_per_zone[z]:
                gen_cap_op_r[pos[h]] = gen_cap_op_r[pos[h]] + \
                    np.array([value(instance.hyb_cap_op[z, h])])
                gen_cap_new_r[pos[h]] = gen_cap_new_r[pos[h]] + \
                    np.array([value(instance.hyb_cap_new[z, h])])

        N = np.arange(len(techsinregion))
        ExCap_r = gen_cap_op_r - gen_cap_new_r
        width = 0.35
        # Plotting instructions
        colour = palette(instance, techsinregion)
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        ax.bar(N, ExCap_r.tolist(), width, color=colour)  # Existing capacity
        ax.bar(N, gen_cap_new_r, width, bottom=ExCap_r,
               color=colour, edgecolor='white', hatch='////')  # New Capacity
        ax.set_xticks(N)
        ax.set_xticklabels([tname[t] for t in techsinregion])
        for tick in ax.get_xticklabels():
            tick.set_rotation(90)
        ax.set_title(rname[r], position=(0.9, 0.9))  # Region names
    # plt.show()
    plt.savefig(results_dir + out  +'/results/' + out  +'_capacity_allgen_'+str(yearyear)+'.png')
def plotevcapacity(instance,out,yearyear):
    """ Stacked plot of capacities
     Feel free to improve the efficiency of this code
    """
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    # cycle through NEM regions`
    for r in instance.regions:
        # gather load for NEM region from solved model instance
        # empty set of all technologies in a region
        evsinregion = _evsinregion(instance, r)
        # gather technology text_ids in region for plot labels
        plabels = []
        for t in evsinregion:
            plabels.append(tname[t])

        # Empty array of gen_cap_op_r
        gen_cap_op_r = np.zeros([len(evsinregion)])
        gen_cap_new_r = np.zeros([len(evsinregion)])
        # positions of each tech in numpy array
        pos = dict(zip(list(evsinregion), range(len(evsinregion))))
        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:

            for e in instance.ev_tech_per_zone[z]: #KP_ADDED
                gen_cap_op_r[pos[e]] = gen_cap_op_r[pos[e]] + \
                    np.array([value(instance.ev_cap_op[z, e])])


        N = np.arange(len(evsinregion))
        ExCap_r = gen_cap_op_r - gen_cap_new_r
        width = 0.35
        # Plotting instructions
        colour = palette(instance, evsinregion)
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        ax.bar(N, ExCap_r.tolist(), width, color=colour)  # Existing capacity
        ax.bar(N, gen_cap_new_r, width, bottom=ExCap_r,
               color=colour, edgecolor='white', hatch='////')  # New Capacity
        ax.set_xticks(N)
        ax.set_xticklabels([tname[t] for t in evsinregion])
        for tick in ax.get_xticklabels():
            tick.set_rotation(90)
        ax.set_title(rname[r], position=(0.9, 0.9))  # Region names
        # plt.legend(handles=[p1, p2], title='title', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='xx-small')
    # plt.show()
    plt.savefig(results_dir + out  +'/results/' + out  +'_ev_capacity_'+str(yearyear)+'.png')
def plot_evs(instance,scen_name,yearyear):
    tname = _get_textid('technology_type')
    for r in instance.regions:
        evsinregion = _evsinregion(instance, r)
        plabels = []
        for t in evsinregion:
            plabels.append(tname[t])
        # print(plabels)
    if len(plabels)>0:
        plotevcapacity(instance, scen_name, instance.name)
        plotevresults_v2g(instance, scen_name, instance.name)
        plotevresults_charge(instance, scen_name, instance.name)
        plotevresults_dumb_charge(instance, scen_name, instance.name)
        plotevresults_smart_charge(instance, scen_name, instance.name)
        plotevresults_transport(instance, scen_name, instance.name)
        save_ev_traces(instance, scen_name, instance.name)
    else:
        print("No EVS to print")
def plotevresults_v2g(instance,out,yearyear): #KP_MODIFIED_070920
    """ Process results to plot.
     Feel free to improve the efficiency of this code
    """
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # Process results to plot.
    # Feel free to improve the efficiency of this code
    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    ts = np.array([t for t in instance.t], dtype=np.datetime64)
    # cycle through NEM regions`
    for r in instance.regions:
        # Set of all technologies in a region
        evsinregion = _evsinregion(instance, r)
        # gather technology text_ids in region for plot labels
        plabels = []
        for t in evsinregion:
            plabels.append(tname[t])
        q_z_r = np.zeros([len(evsinregion), len(instance.t)])
        # positions of each tech in numpy array
        pos = dict(zip(list(evsinregion), range(len(evsinregion))))
        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            for e in instance.ev_tech_per_zone[z]: #KP_ADDED #KP_QUESTION - should dispatch be included for evs? #KP_TO_DO_LATER
                q_z_r[pos[e], :] = q_z_r[pos[e], :] + \
                    np.array([value(instance.ev_v2g_disp[z, e, t])
                              for t in instance.t])

        # Plotting instructions
        # pick respective subplot
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        palr = palette(instance, evsinregion)
        ax.stackplot(ts, q_z_r, colors=palr)  # dispatch values
        # ax.plot(ts, load, color='black')  # Put load on top
        ax.legend(plabels)  # put labels
        ax.set_title(rname[r])  # Region names

        fig.autofmt_xdate()
    # plt.show()
    plt.savefig(results_dir + out  +'/results/' + out  +'_v2g_'+str(yearyear)+'.png')
def plotevresults_charge(instance,out,yearyear):
    """ Process results to plot.
     Feel free to improve the efficiency of this code
    """
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # Process results to plot.
    # Feel free to improve the efficiency of this code
    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    ts = np.array([t for t in instance.t], dtype=np.datetime64)
    # cycle through NEM regions`
    for r in instance.regions:
        # Set of all technologies in a region
        evsinregion = _evsinregion(instance, r)
        # gather technology text_ids in region for plot labels
        plabels = []
        for t in evsinregion:
            plabels.append(tname[t])
        q_z_r = np.zeros([len(evsinregion), len(instance.t)])
        # positions of each tech in numpy array
        pos = dict(zip(list(evsinregion), range(len(evsinregion))))
        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            for e in instance.ev_tech_per_zone[z]: #KP_ADDED #KP_QUESTION - should dispatch be included for evs? #KP_TO_DO_LATER
                q_z_r[pos[e], :] = q_z_r[pos[e], :] + \
                    np.array([value(instance.ev_charge[z, e, t])
                              for t in instance.t])

        # Plotting instructions
        # pick respective subplot
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        palr = palette(instance, evsinregion)
        ax.stackplot(ts, q_z_r, colors=palr)  # dispatch values
        # ax.plot(ts, load, color='black')  # Put load on top
        ax.legend(plabels)  # put labels
        ax.set_title(rname[r])  # Region names

        fig.autofmt_xdate()
    # plt.show()
    plt.savefig(results_dir + out  +'/results/' + out  +'_charge_total_'+str(yearyear)+'.png')
def plotevresults_dumb_charge(instance,out,yearyear):
    """ Process results to plot.
     Feel free to improve the efficiency of this code
    """
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # Process results to plot.
    # Feel free to improve the efficiency of this code
    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    ts = np.array([t for t in instance.t], dtype=np.datetime64)
    # cycle through NEM regions`
    for r in instance.regions:
        # Set of all technologies in a region
        evsinregion = _evsinregion(instance, r)
        # gather technology text_ids in region for plot labels
        plabels = []
        for t in evsinregion:
            plabels.append(tname[t])
        q_z_r = np.zeros([len(evsinregion), len(instance.t)])
        # positions of each tech in numpy array
        pos = dict(zip(list(evsinregion), range(len(evsinregion))))
        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            for e in instance.ev_tech_per_zone[z]: #KP_ADDED #KP_QUESTION - should dispatch be included for evs? #KP_TO_DO_LATER
                q_z_r[pos[e], :] = q_z_r[pos[e], :] + \
                    np.array([value(instance.ev_dumb_charge[z, e, t])
                              for t in instance.t])

        # Plotting instructions
        # pick respective subplot
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        palr = palette(instance, evsinregion)
        ax.stackplot(ts, q_z_r, colors=palr)  # dispatch values
        # ax.plot(ts, load, color='black')  # Put load on top
        ax.legend(plabels)  # put labels
        ax.set_title(rname[r])  # Region names

        fig.autofmt_xdate()
    # plt.show()
    plt.savefig(results_dir + out  +'/results/' + out  +'_charge_dumb_'+str(yearyear)+'.png')
def plotevresults_smart_charge(instance,out,yearyear):
    """ Process results to plot.
     Feel free to improve the efficiency of this code
    """
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # Process results to plot.
    # Feel free to improve the efficiency of this code
    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    ts = np.array([t for t in instance.t], dtype=np.datetime64)
    # cycle through NEM regions`
    for r in instance.regions:
        # Set of all technologies in a region
        evsinregion = _evsinregion(instance, r)
        # gather technology text_ids in region for plot labels
        plabels = []
        for t in evsinregion:
            plabels.append(tname[t])
        q_z_r = np.zeros([len(evsinregion), len(instance.t)])
        # positions of each tech in numpy array
        pos = dict(zip(list(evsinregion), range(len(evsinregion))))
        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            for e in instance.ev_tech_per_zone[z]: #KP_ADDED #KP_QUESTION - should dispatch be included for evs? #KP_TO_DO_LATER
                q_z_r[pos[e], :] = q_z_r[pos[e], :] + \
                    np.array([value(instance.ev_smart_charge[z, e, t])
                              for t in instance.t])

        # Plotting instructions
        # pick respective subplot
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        palr = palette(instance, evsinregion)
        ax.stackplot(ts, q_z_r, colors=palr)  # dispatch values
        # ax.plot(ts, load, color='black')  # Put load on top
        ax.legend(plabels)  # put labels
        ax.set_title(rname[r])  # Region names

        fig.autofmt_xdate()
    # plt.show()
    plt.savefig(results_dir + out  +'/results/' + out  +'_charge_smart_'+str(yearyear)+'.png')
def plotevresults_transport(instance,out,yearyear):
    """ Process results to plot.
     Feel free to improve the efficiency of this code
    """
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    # Process results to plot.
    # Feel free to improve the efficiency of this code
    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    ts = np.array([t for t in instance.t], dtype=np.datetime64)
    # cycle through NEM regions`
    for r in instance.regions:
        # Set of all technologies in a region
        evsinregion = _evsinregion(instance, r)
        # gather technology text_ids in region for plot labels
        plabels = []
        for t in evsinregion:
            plabels.append(tname[t])
        q_z_r = np.zeros([len(evsinregion), len(instance.t)])
        # positions of each tech in numpy array
        pos = dict(zip(list(evsinregion), range(len(evsinregion))))
        # collect the total dispatch for each technology across Zones in region
        for z in instance.zones_per_region[r]:
            for e in instance.ev_tech_per_zone[z]: #KP_ADDED #KP_QUESTION - should dispatch be included for evs? #KP_TO_DO_LATER
                q_z_r[pos[e], :] = q_z_r[pos[e], :] + \
                    np.array([value(instance.ev_disp_transport[z, e, t])
                              for t in instance.t])

        # Plotting instructions
        # pick respective subplot
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        palr = palette(instance, evsinregion)
        ax.stackplot(ts, q_z_r, colors=palr)  # dispatch values
        # ax.plot(ts, load, color='black')  # Put load on top
        ax.legend(plabels)  # put labels
        ax.set_title(rname[r])  # Region names

        fig.autofmt_xdate()
    # plt.show()
    plt.savefig(results_dir + out  +'/results/' + out  +'_transport_'+str(yearyear)+'.png')
def plotDemandtrace(instance,out,yearyear):  # pragma: no cover #KP_MODIFIED_170820
    tname = _get_textid('technology_type')
    rname = _get_textid('region')

    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    ts = np.array([t for t in instance.t], dtype=np.datetime64)
    # cycle through NEM regions`
    for r in instance.regions:
        # Set of all technologies in a region
        techsinregion = _techsinregion(instance, r)
        plabels = ["net_demand","net_demand_less_evs"]

        # gather load for NEM region from solved model instance
        load = np.array([value(instance.region_net_demand[r, t])
                         for t in instance.t])
        load_less_evs = np.array([value(instance.region_net_demand_less_evs[r, t])
                         for t in instance.t]) #KP_MODIFIED_170820
        # aemo_ev_load = np.array([value(instance.aemo_ev[r, t]) #KP_MODIFIED_170820
                         # for t in instance.t])

        # Plotting instructions
        # pick respective subplot
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        palr = palette(instance, techsinregion)
        # ax.stackplot(ts, q_z_r, colors=palr)  # dispatch values
        ax.plot(ts, load, color='black')  # Put load on top
        ax.plot(ts, load_less_evs, color='red')  #KP_MODIFIED_170820
        # ax.plot(ts, aemo_ev_load, color='purple')  #KP_MODIFIED_170820
        ax.legend(plabels)  # put labels
        ax.set_title(rname[r])  # Region names
def plotAEMOEVtrace(instance,out,yearyear):  # pragma: no cover #KP_MODIFIED_170820
    tname = _get_textid('technology_type')
    rname = _get_textid('region')

    # create set of plots that fits all NEM regions
    fig = plt.figure(figsize=(14, 9))
    # horizontal axis with timesamps
    ts = np.array([t for t in instance.t], dtype=np.datetime64)
    # cycle through NEM regions`
    for r in instance.regions:
        # Set of all technologies in a region
        techsinregion = _techsinregion(instance, r)

        plabels = ["aemo_ev_demand"]

        aemo_ev_load = np.array([value(instance.aemo_ev[r, t]) #KP_MODIFIED_170820
                         for t in instance.t])

        # Plotting instructions
        # pick respective subplot
        if r % 2 == 0:
            ax = fig.add_subplot(2, 2, r)
        else:
            ax = fig.add_subplot(3, 2, r)
        palr = palette(instance, techsinregion)
        ax.plot(ts, aemo_ev_load, color='purple')  #KP_MODIFIED_170820
        ax.legend(plabels)  # put labels
        ax.set_title(rname[r])  # Region names

        fig.autofmt_xdate()
    # plt.show()
    # KP_MODIFIED to save to file rather than pause the program and display
    # plt.savefig('E:/OneDrive - UNSW/PhD/Modelling/OpenCEM_EVBranch_KP/openCEM/' + out + '/results/' + out  +'_dispatch_allgen_'+str(yearyear)+'.png')
    plt.savefig(results_dir + out  +'/results/' + out  +'_demand_aemo_evs_'+str(yearyear)+'.png')
def plotcluster(cluster, row=3, col=4, ylim=None, show=False):  # pragma: no cover
    '''Plot cluster result from full set of weeks, cluster weeks and weights'''
    t = range(1, cluster.nplen + 1)
    # Make  row * col subplots
    axarr = plt.subplots(row, col, sharex=True)[1]
    # Plot each observation in their respective cluster plot
    for i in range(cluster.periods):
        axarr.flat[cluster.cluster[i]
                   - 1].plot(t, cluster.X[i][:cluster.nplen], '0.01', alpha=0.3, linewidth=0.75)

    # Add mean and nearest incluster for each cluster plit
    plotrange = cluster.max_d - 2 if isinstance(cluster,cemo.cluster.InstanceCluster) else cluster.max_d
    for j in range(plotrange):

        axarr.flat[j].plot(t, cluster.Xsynth[j], 'r')  # mean
        axarr.flat[j].plot(t,
                           cluster.X[cluster.Xcluster['week']
                                     [j] - 1][:cluster.nplen],
                           'k',
                           # linestyle='None',
                           # marker='+'
                           )  # closest observation
    # make yrange the same in all plots
    for ax in axarr.flat:
        if ylim is None:
            # default
            ax.set_ylim(0, 16000)
        else:
            ax.set_ylim(ylim[0], ylim[1])
    # Show results
    plt.savefig(results_dir + out  +'/results/' + out  +'_cluster_'+str(yearyear)+'.png')
    # if show:
    #     plt.show()
    return plt

# Print results on cmd terminal
def _printcosts(inst):
    locale.setlocale(locale.LC_ALL, 'en_AU.UTF-8')
    print("Total Cost:\t %20s" %
          locale.currency(value(cemo.rules.system_cost(inst)), grouping=True))
    print("Build cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_capital(inst)),
                          grouping=True))
    print("Repayment cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_repayment(inst)),
                          grouping=True))
    print("Operating cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_operating(inst)),
                          grouping=True))
    print("Fixed cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_fixed(inst)),
                          grouping=True))
    print("Trans. build cost:\t %12s" %
          locale.currency(value(cemo.rules.cost_trans_build(inst)),
                          grouping=True))
    print("Trans. flow cost:\t %12s" %
          locale.currency(value(cemo.rules.cost_trans_flow(inst)),
                          grouping=True))
    print("Unserved cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_unserved(inst)),
                          grouping=True))
    print("Emission cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_emissions(inst)),
                          grouping=True))
    print("Retirmt cost:\t %20s" %
          locale.currency(value(cemo.rules.cost_retirement(inst)),
                          grouping=True))
    print("V2G Payments @ 10c/kWh ($100/MWh):\t %20s" %
          locale.currency(value(cemo.rules.cost_v2g_payments(inst)),
                          grouping=True))
    print("Smart Payments @ 10c/kWh ($100/MWh):\t %20s" %
          locale.currency(value(cemo.rules.cost_smart_payments(inst)),
                          grouping=True))
    print("year_correction_factor:\t %s" % value(inst.year_correction_factor(inst)))
def _printemissionrate(instance):
    emrate = sum(value(cemo.rules.emissions(instance, r))
                 for r in instance.regions) /\
        (sum(value(cemo.rules.dispatch(instance, r)) for r in instance.regions) + 1.0e-12)
    print("Total Emission rate: %6.3f kg/MWh" % emrate)
def _printunserved(instance):
    regions = list(instance.regions)
    unserved = np.zeros(len(regions), dtype=float)
    for region in regions:
        unserved[regions.index(region)] \
            = 100.0 * sum(value(instance.unserved[zone, time])
                          for zone in instance.zones_per_region[region]
                          for time in instance.t) \
            / sum(value(instance.region_net_demand_less_evs[region, time]) for time in instance.t)

    print('Unserved %:' + str(unserved))
def _printcapacity(instance):
    tname = _get_textid('technology_type')
    hours = float(len(instance.t))
    techtotal = [0] * len(instance.all_tech)
    disptotal = [0] * len(instance.all_tech)
    capftotal = [0] * len(instance.all_tech)
    nperz = [0] * len(instance.all_tech)
    idx = list(instance.all_tech)
    for z in instance.zones:
        for n in instance.gen_tech_per_zone[z]:
            techtotal[idx.index(n)] += value(instance.gen_cap_op[z, n])
            disptotal[idx.index(n)] += value(sum(1e3 * instance.gen_disp[z, n, t]
                                                 for t in instance.t))
            capftotal[idx.index(n)] += value(sum(instance.gen_cap_factor[z, n, t]
                                                 for t in instance.t))
            nperz[idx.index(n)] += 1
        for s in instance.stor_tech_per_zone[z]:
            techtotal[idx.index(s)] += value(instance.stor_cap_op[z, s])
            disptotal[idx.index(s)] += value(sum(1e3 * instance.stor_disp[z, s, t]
                                                 for t in instance.t))
            capftotal[idx.index(s)] += 0.5 * hours
            nperz[idx.index(s)] += 1

        for h in instance.hyb_tech_per_zone[z]:
            techtotal[idx.index(h)] += value(instance.hyb_cap_op[z, h])
            disptotal[idx.index(h)] += value(sum(1e3 * instance.hyb_disp[z, h, t]
                                                 for t in instance.t))
            capftotal[idx.index(h)] += value(sum(instance.hyb_cap_factor[z, h, t]
                                                 for t in instance.t))
            nperz[idx.index(h)] += 1

    NEMcap = sum(techtotal)
    NEMdis = sum(disptotal)
    print("NEM Capacity total: %sW\tNEM Dispatch total: %sWh" % (
          si_format(NEMcap * 1e6, precision=2),
          si_format(NEMdis * 1e6, precision=2)
          ))

    for j in instance.all_tech:
        if techtotal[idx.index(j)] > 0:
            print("%17s: %7sW | dispatch: %7sWh | avg cap factor: %.2f(%.2f)" % (
                tname[j],
                si_format(techtotal[idx.index(j)] * 1e6, precision=1),
                si_format(disptotal[idx.index(j)] * 1e6, precision=1),
                disptotal[idx.index(j)] / hours / techtotal[idx.index(j)],
                capftotal[idx.index(j)] / hours / nperz[idx.index(j)]
            ))
def _printevs(instance):
    tname = _get_textid('technology_type')
    hours = float(len(instance.t))
    evtechtotal = [0] * len(instance.all_tech)
    evdisptotal = [0] * len(instance.all_tech)
    evdisptranstotal = [0] * len(instance.all_tech)
    evchargetotal = [0] * len(instance.all_tech)
    evdumbtotal = [0] * len(instance.all_tech)
    evsmarttotal = [0] * len(instance.all_tech)
    evincentivetotal = [0] * len(instance.all_tech)
    evnperz = [0] * len(instance.all_tech)
    idx = list(instance.all_tech)
    for z in instance.zones:
        # print(" ZONE: {}".format(z))
        for e in instance.ev_tech_per_zone[z]: #KP_ADDED
            evtechtotal[idx.index(e)] += value(instance.ev_cap_op[z, e])
            evdisptotal[idx.index(e)] += value(sum(instance.ev_v2g_disp[z, e, t]
                                                 for t in instance.t))
            evdisptranstotal[idx.index(e)] += value(sum(instance.ev_disp_transport[z, e, t]
                                                 for t in instance.t))
            evchargetotal[idx.index(e)] += value(sum(instance.ev_charge[z, e, t]
                                                 for t in instance.t))
            evdumbtotal[idx.index(e)] += value(sum(instance.ev_dumb_charge[z, e, t] #KP_Question: should I model this more like the hybrid or storage?? #KP_TO_DO_LATER
                                                 for t in instance.t))
            evsmarttotal[idx.index(e)] += value(sum(instance.ev_smart_charge[z, e, t] #KP_Question: should I model this more like the hybrid or storage?? #KP_TO_DO_LATER
                                                 for t in instance.t))
            # evincentivetotal[idx.index(e)] += value(sum(instance.ev_smart_charge[z, e, t] #KP_Question: should I model this more like the hybrid or storage?? #KP_TO_DO_LATER
            #                                      for t in instance.t)) * instance.cost_ev_vom[e]

            # print("EV %s:   Cap: %sWh | Charge: %sWh | Transport: %sWh" % (e,si_format(value(instance.ev_cap_op[z, e]) * 1e6, precision=2), si_format(value(sum(instance.ev_charge[z, e, t] for t in instance.t))* 1e6, precision=2), si_format(value(sum(instance.ev_disp_transport[z, e, t] for t in instance.t))* 1e6, precision=2)))

            evnperz[idx.index(e)] += 1
    evNEMcap = sum(evtechtotal)
    evNEMdis = sum(evdisptotal)
    evNEMdisTrans = sum(evdisptranstotal)
    evNEMcharge = sum(evchargetotal)
    evNEMdumbcharge = sum(evdumbtotal)
    evNEMsmartcharge = sum(evsmarttotal)
    # evNEMincentive = sum(evincentivetotal)

    # print("\n **************** EVS ******************* ")
    print("EV NEM Capacity total: %sWh \nEV NEM V2G Dispatch total: %sWh | EV NEM Transport Dispatch total: %sWh\nEV NEM Charge total: %sWh | EV NEM DUMB Charge total: %sWh | EV NEM SMART Charge total: %sWh" % (
          si_format(evNEMcap * 1e6, precision=2),
          si_format(evNEMdis * 1e6, precision=2),
          si_format(evNEMdisTrans * 1e6, precision=2),
          si_format(evNEMcharge * 1e6, precision=2),
          si_format(evNEMdumbcharge * 1e6, precision=2),
          si_format(evNEMsmartcharge * 1e6, precision=2)
          ))

    # for j in instance.all_tech:
    #     if evtechtotal[idx.index(j)] > 0:
    #         print("%17s: %7sW | V2G dispatch: %7sWh | Transport dispatch: %7sWh | Charge: %7sWh | DUMB Charge: %7sWh | SMART Charge: %7sWh" % (
    #             tname[j],
    #             si_format(evtechtotal[idx.index(j)] * 1e6, precision=1),
    #             si_format(evdisptotal[idx.index(j)] * 1e6, precision=1),
    #             si_format(evdisptranstotal[idx.index(j)] * 1e6, precision=1),
    #             si_format(evchargetotal[idx.index(j)] * 1e6, precision=1),
    #             si_format(evdumbtotal[idx.index(j)] * 1e6, precision=1),
    #             si_format(evsmarttotal[idx.index(j)] * 1e6, precision=1),
    #         ))
    return
def _print_starting_conds(instance):
        tname = _get_textid('technology_type')
        hours = float(len(instance.t))
        techtotal = [0] * len(instance.all_tech)
        nperz = [0] * len(instance.all_tech)
        idx = list(instance.all_tech)
        for z in instance.zones:
            for n in instance.gen_tech_per_zone[z]:
                techtotal[idx.index(n)] += value(instance.gen_cap_initial[z, n])
                nperz[idx.index(n)] += 1
            for s in instance.stor_tech_per_zone[z]:
                techtotal[idx.index(s)] += value(instance.stor_cap_initial[z, s])
                nperz[idx.index(s)] += 1
            for h in instance.hyb_tech_per_zone[z]:
                techtotal[idx.index(h)] += value(instance.hyb_cap_initial[z, h])
                nperz[idx.index(h)] += 1

        NEMcap = sum(techtotal)
        print("NEM Starting Capacity: %sW" % (
              si_format(NEMcap * 1e6, precision=2)
              ))

        for j in instance.all_tech:
            if techtotal[idx.index(j)] > 0:
                print("%17s: %7sW" % (
                    tname[j],
                    si_format(techtotal[idx.index(j)] * 1e6, precision=1)
                ))
def _print_retirements(instance):
        tname = _get_textid('technology_type')
        hours = float(len(instance.t))
        techtotal = [0] * len(instance.all_tech)
        nperz = [0] * len(instance.all_tech)
        idx = list(instance.all_tech)
        for z in instance.zones:
            for n in instance.gen_tech_per_zone[z]:
                techtotal[idx.index(n)] += value(instance.gen_cap_ret[z, n])
                nperz[idx.index(n)] += 1

        NEMcap = sum(techtotal)
        print("NEM Retired Capacity: %sW" % (
              si_format(NEMcap * 1e6, precision=2)
              ))

        for j in instance.all_tech:
            if techtotal[idx.index(j)] > 0:
                print("%17s: %7sW" % (
                    tname[j],
                    si_format(techtotal[idx.index(j)] * 1e6, precision=1)
                ))

# Master
def printstats(instance,scen_name,yearyear):
    """Print results on screen """
    _printcapacity(instance)
    _printcosts(instance)
    _printunserved(instance)
    _printemissionrate(instance)
    _printevs(instance)
    # _print_starting_conds(instance)
    # plotcluster(instance)

    """Save results to file """
    save_results(instance, scen_name, instance.name)
    save_ev_results(instance, scen_name, instance.name)
    save_gen_traces(instance,scen_name,yearyear)
    save_load_traces(instance,scen_name,yearyear)
    save_intercon_traces(instance,scen_name,yearyear)
    save_cap_zone_results(instance,scen_name,yearyear)
    save_intercon_cap_zone_results(instance,scen_name,yearyear)
    save_ev_cap_zone_results(instance,scen_name,yearyear)
    # save_ev_overall_results(instance,scen_name,yearyear)
    save_ev_traces(instance, scen_name, instance.name)

    """Plot results to file """
    plotresults(instance, scen_name, instance.name)
    # plotcapacity(instance, scen_name, instance.name)
    plot_evs(instance,scen_name,yearyear)

    print("*************End of results for %s***************** \n" % instance.name, flush=True)
