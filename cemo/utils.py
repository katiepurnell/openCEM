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

import cemo.const
import cemo.rules

results_dir = "E:/OneDrive - UNSW/PhD/Modelling/openCEMKP/scenarios/" #KP_MODIFIED
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
        load = np.array([value(instance.region_net_demand[r, t])
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
def save_results(inst, out,yearyear): #KP_MODIFIED - this section is from Dan
    tname = _get_textid('technology_type')
    rname = _get_textid('region')
    hours = float(len(inst.t))
    techtotal = [0] * len(inst.all_tech)
    disptotal = [0] * len(inst.all_tech)
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
            disptotal[idx.index(e)] += value(sum(inst.ev_v2g_disp[z, e, t]
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
    df['Nem Cap Total'] = [sum(techtotal)]
    df['Nem Disp Total'] = [sum(disptotal)]
    for r in inst.regions:
        load = sum(inst.region_net_demand[r, t] for t in inst.t) #(np.array([value(inst.region_net_demand[r, t]) for t in inst.t]))
        # load_less_evs = sum(inst.region_net_demand_less_evs[r, t] for t in inst.t) #KP_MODIFIED_170820
        # aemo_ev_load = sum(inst.aemo_ev[r, t] for t in inst.t) #KP_MODIFIED_170820
        # df['Total Load'] = [sum(load)/1000]
        df['Load_'+str(rname[r])] = [load] #[sum(load)/1000]
        # df['Load_less_evs'+str(rname[r])] = [load_less_evs] #KP_MODIFIED_170820
        # df['Load_aemo_ev'+str(rname[r])] = [aemo_ev_load] #KP_MODIFIED_170820

    for j in inst.all_tech:
        if techtotal[idx.index(j)] > 0:
            df['Capcity'+str(tname[j])] = [techtotal[idx.index(j)] * 1e6]
            df['dispatch'+str(tname[j])] = [disptotal[idx.index(j)] * 1e6]
            df['avg cap factor'+str(tname[j])] = [disptotal[idx.index(j)] / hours / techtotal[idx.index(j)]* 1e3]

    # df['Total Cost'] = [locale.currency(value(inst.Obj - cemo.rules.cost_shadow(inst)))]

    df['Total Cost'] = [locale.currency(value(cemo.rules.system_cost(inst)))]
    df['Shadow Costs'] = [locale.currency(value(cemo.rules.cost_shadow(inst)))]
    df['Dan Obj Less Shadow'] = [locale.currency(value(inst.Obj - cemo.rules.cost_shadow(inst)))]

    df["Overall LCOE"] = [locale.currency(value((inst.Obj - cemo.rules.cost_shadow(inst)) / sum(inst.region_net_demand[r, t]
                                                                                for r in inst.regions
                                                                                for t in inst.t)))]

    df["Total Build Cost"] = [locale.currency(value(cemo.rules.cost_capital(inst)))]
    df["Build cost endo"]=[locale.currency(sum(value(cemo.rules.cost_build_per_zone_model(inst, zone) - inst.cost_cap_carry_forward[zone]) for zone in inst.zones))]
    df["Build cost exo"]=[locale.currency(sum(value(cemo.rules.cost_build_per_zone_exo(inst, zone) - inst.cost_cap_carry_forward[zone]) for zone in inst.zones))]

    df["Repayment cost"]=[locale.currency(value(sum(inst.cost_cap_carry_forward[z] for z in inst.zones)))]
    df["Operating cost"] =[locale.currency(value(cemo.rules.cost_operating(inst)))]
    df["Fixed cost"] =[locale.currency(value(cemo.rules.cost_fixed(inst)))]
    df["Trans. build cost"]= [locale.currency(value(cemo.rules.cost_trans_build(inst)))]

    df["Trans. build cost endo"]=[locale.currency(sum(value(cemo.rules.cost_trans_build_per_zone_model(inst, zone)) for zone in inst.zones))]
    df["Trans. build cost endo"]=[locale.currency(sum(value(cemo.rules.cost_trans_build_per_zone_exo(inst, zone)) for zone in inst.zones))]
    df["Trans. flow cost"]=[locale.currency(value(cemo.rules.cost_trans_flow(inst)))]
    df["Unserved cost"]=[locale.currency(value(cemo.rules.cost_unserved(inst)))]

    df["Emission cost"]=[locale.currency(value(cemo.rules.cost_emissions(inst)))]
    df["Retirmt cost"]=[locale.currency(value(cemo.rules.cost_retirement(inst)))]

    total_emissions = 0
    total_dispatch = 0
    for r in inst.regions:
        total_emissions = total_emissions + value(cemo.rules.emissions(inst, r))
        total_dispatch = total_dispatch + value(cemo.rules.dispatch(inst, r))
    emrate = total_emissions/(total_dispatch+ 1.0e-12) # so its not dividing by 0
    df["Emissions rate kg MWh"]=[emrate]

    # for r in inst.regions:
    #     for z in inst.zones_per_region[r]:
    #         for n in inst.gen_tech_per_zone[z]:
    #             df["LCOE Cost" + str(tname[n])] = [locale.currency(value(cemo.rules.cost_lcoe(inst, n)))]
    #         for s in inst.stor_tech_per_zone[z]:
    #             df["LCOE Cost" + str(tname[s])] = [locale.currency(value(cemo.rules.cost_lcoe(inst, s)))]
    #         for e in inst.ev_tech_per_zone[z]:
    #             df["LCOE Cost" + str(tname[e])] = [locale.currency(value(cemo.rules.cost_lcoe(inst, e)))]
    df.to_csv(results_dir + out  +'/results/' +out+'_results_'+str(yearyear)+'.csv')

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
            / sum(value(instance.region_net_demand[region, time]) for time in instance.t)

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
        print(" ZONE: {}".format(z))
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
            evincentivetotal[idx.index(e)] += value(sum(instance.ev_smart_charge[z, e, t] #KP_Question: should I model this more like the hybrid or storage?? #KP_TO_DO_LATER
                                                 for t in instance.t)) * instance.cost_ev_vom[e]

            print("EV %s:   Cap: %sWh | Charge: %sWh | Transport: %sWh" % (e,si_format(value(instance.ev_cap_op[z, e]) * 1e6, precision=2), si_format(value(sum(instance.ev_charge[z, e, t] for t in instance.t))* 1e6, precision=2), si_format(value(sum(instance.ev_disp_transport[z, e, t] for t in instance.t))* 1e6, precision=2)))

            evnperz[idx.index(e)] += 1
    evNEMcap = sum(evtechtotal)
    evNEMdis = sum(evdisptotal)
    evNEMdisTrans = sum(evdisptranstotal)
    evNEMcharge = sum(evchargetotal)
    evNEMdumbcharge = sum(evdumbtotal)
    evNEMsmartcharge = sum(evsmarttotal)
    evNEMincentive = sum(evincentivetotal)

    print("\n **************** EVS ******************* ")
    print("EV NEM Capacity total: %sWh\nEV NEM V2G Dispatch total: %sWh\nEV NEM Transport Dispatch total: %sWh\nEV NEM Charge total: %sWh\nEV NEM DUMB Charge total: %sWh\nEV NEM SMART Charge total: %sWh\nEV Incentive payments ( @ $10/kWh): $ %s" % (
          si_format(evNEMcap * 1e6, precision=2),
          si_format(evNEMdis * 1e6, precision=2),
          si_format(evNEMdisTrans * 1e6, precision=2),
          si_format(evNEMcharge * 1e6, precision=2),
          si_format(evNEMdumbcharge * 1e6, precision=2),
          si_format(evNEMsmartcharge * 1e6, precision=2),
          si_format(evNEMincentive, precision=2)
          ))

    for j in instance.all_tech:
        if evtechtotal[idx.index(j)] > 0:
            print("%17s: %7sW | V2G dispatch: %7sWh | Transport dispatch: %7sWh | Charge: %7sWh | DUMB Charge: %7sWh | SMART Charge: %7sWh" % (
                tname[j],
                si_format(evtechtotal[idx.index(j)] * 1e6, precision=1),
                si_format(evdisptotal[idx.index(j)] * 1e6, precision=1),
                si_format(evdisptranstotal[idx.index(j)] * 1e6, precision=1),
                si_format(evchargetotal[idx.index(j)] * 1e6, precision=1),
                si_format(evdumbtotal[idx.index(j)] * 1e6, precision=1),
                si_format(evsmarttotal[idx.index(j)] * 1e6, precision=1),
            ))

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

def printstats(instance,scen_name,yearyear):
    """Print summary of results for model instance"""
    _printcapacity(instance)
    _printcosts(instance)
    _printunserved(instance)
    _printemissionrate(instance)
    _print_starting_conds(instance)
    _printevs(instance)
    # plotcluster(instance)
    save_gen_traces(instance,scen_name,yearyear)
    save_load_traces(instance,scen_name,yearyear)

    plotresults(instance, scen_name, instance.name)
    save_results(instance, scen_name, instance.name)
    plotcapacity(instance, scen_name, instance.name)

    plot_evs(instance,scen_name,yearyear)


    print("End of results for %s" % instance.name, flush=True)

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
        load = np.array([value(instance.region_net_demand[r, t])
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
