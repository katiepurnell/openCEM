"""Module to host all the rules applied to model"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"

from pyomo.environ import Constraint, value

import cemo.const


def region_in_zone(zone):
    '''Return region where a given zone belongs to'''
    result = [pair[0] for pair in cemo.const.ZONES_IN_REGIONS if pair[1] == zone]
    return result[0]


def ScanForTechperZone(model):
    '''generate sparse generator zone sets from tuple based sets'''
    for (i, j) in model.gen_tech_in_zones:
        model.gen_tech_per_zone[i].add(j)
    for (i, j) in model.retire_gen_tech_in_zones:
        model.retire_gen_tech_per_zone[i].add(j)
    for (i, j) in model.fuel_gen_tech_in_zones:
        model.fuel_gen_tech_per_zone[i].add(j)
    for (i, j) in model.commit_gen_tech_in_zones:
        model.commit_gen_tech_per_zone[i].add(j)
    for (i, j) in model.re_gen_tech_in_zones:
        model.re_gen_tech_per_zone[i].add(j)
    for (i, j) in model.disp_gen_tech_in_zones:
        model.disp_gen_tech_per_zone[i].add(j)
    for (i, j) in model.re_disp_gen_tech_in_zones:
        model.re_disp_gen_tech_per_zone[i].add(j)


def ScanForStorageperZone(model):
    '''generate sparse storage zone sets from tuple based sets'''
    for (i, j) in model.stor_tech_in_zones:
        model.stor_tech_per_zone[i].add(j)


def ScanForHybridperZone(model):
    '''generate hybrid generator zone sets from tuple based sets'''
    for (i, j) in model.hyb_tech_in_zones:
        model.hyb_tech_per_zone[i].add(j)

def ScanForEVperZone(model):
    '''generate ev generator zone sets from tuple based sets'''
    for (i, j) in model.ev_tech_in_zones:
        model.ev_tech_per_zone[i].add(j)

def ScanForZoneperRegion(model):
    '''Generate tuples of zones in regions based on default or configured data'''
    for (i, j) in model.zones_in_regions:
        if i in model.regions:
            model.zones_per_region[i].add(j)


def build_intercon_per_zone(model):
    '''Generate (source,target) interconnector tuples based on default or supplied data'''
    for (i, j) in model.intercons_in_zones:
        model.intercon_per_zone[i].add(j)


def build_carry_fwd_cost_per_zone(model):
    '''Generate cost_cap_carry_forward from historical and simulated values'''
    for zone in model.zones:
        model.cost_cap_carry_forward[zone] = model.cost_cap_carry_forward_sim[
            zone] + model.cost_cap_carry_forward_hist[zone]


def build_cap_factor_thres(model):
    '''Make hourly generation factors below threshold equal to zero'''
    for zone in model.zones:
        for time in model.t:
            for tech in model.gen_tech_per_zone[zone]:
                if value(model.gen_cap_factor[zone, tech, time]) < cemo.const.CAP_FACTOR_THRES:
                    model.gen_cap_factor[zone, tech, time] = 0
            for tech in model.hyb_tech_per_zone[zone]:
                if value(model.hyb_cap_factor[zone, tech, time]) < cemo.const.CAP_FACTOR_THRES:
                    model.hyb_cap_factor[zone, tech, time] = 0


def dispatch(model, r):
    '''calculate sum of all dispatch'''
    return sum(1e3*model.gen_disp[z, n, t]
               for z in model.zones_per_region[r]
               for n in model.gen_tech_per_zone[z]
               for t in model.t)\
        + sum(1e3*model.stor_disp[z, s, t]
              for z in model.zones_per_region[r]
              for s in model.stor_tech_per_zone[z]
              for t in model.t)\
        + sum(1e3*model.hyb_disp[z, h, t]
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              for t in model.t)\
        + sum(model.ev_v2g_disp[z, e, t] #KP_MODIFIED_310820 from ev_disp to ev_v2g_disp
              for z in model.zones_per_region[r]
              for e in model.ev_tech_per_zone[z]
              for t in model.t)


def emissions(model, r):
    '''calculate emissions in kg'''
    return (sum(model.fuel_emit_rate[n] * 1e3*model.gen_disp[z, n, t]
                for z in model.zones_per_region[r]
                for n in model.fuel_gen_tech_per_zone[z]
                for t in model.t)
            + sum(model.fuel_emit_rate[n] * 1e3*model.gen_disp_com_p[z, n, t]
                  for z in model.zones_per_region[r]
                  for n in model.commit_gen_tech_per_zone[z]
                  for t in model.t))


def con_nem_ret_ratio(model):
    '''inequality constraint defining renewable generation must be greater
       or equal than total generation times ret ratio'''
    return sum(model.gen_disp[z, n, t]
               for r in model.regions
               for z in model.zones_per_region[r]
               for n in model.re_gen_tech_per_zone[z]
               for t in model.t
               )\
        + sum(model.hyb_disp[z, h, t]
              for r in model.regions
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              for t in model.t
              )\
        >= model.nem_ret_ratio * (
        sum(model.gen_disp[z, n, t]
            for r in model.regions
            for z in model.zones_per_region[r]
            for n in model.gen_tech_per_zone[z]
            for t in model.t
            )
        + sum(model.hyb_disp[z, h, t]
              for r in model.regions
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              for t in model.t
              )
    )


def con_nem_ret_gwh(model):
    '''inequality constraint setting renewable generation must be greater or equal
    than a defined GWh per year across the system'''
    return sum(model.gen_disp[z, n, t]
               for r in model.regions
               for z in model.zones_per_region[r]
               for n in model.re_gen_tech_per_zone[z]
               for t in model.t
               )\
        + sum(model.hyb_disp[z, h, t]
              for r in model.regions
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              for t in model.t
              )\
        >= model.nem_ret_gwh / model.year_correction_factor


def con_operating_reserve(model, region, time):
    '''Operating reserve margin for each NEM region

    At each hour, reserves consist of the sum of:
    -spare capacity from dispatchable flexible genenerators
    -spare committed capacity from non flexible generators
    -spare capacity from storage (considering charge),
    -spare capacity from hybrids (considering charge),
    storage and hybrids must be greater or equal than a percentage
    of the load, determined by the `operating_reserve` parameter'''
    return sum(model.gen_cap_op[zone, gen_tech] - 1e3*model.gen_disp[zone, gen_tech, time]
               for zone in model.zones_per_region[region]
               for gen_tech in set(model.disp_gen_tech_per_zone[zone])
               - set(model.commit_gen_tech_per_zone[zone])
               )\
        + sum(1e3*model.gen_disp_com[zone, gen_tech, time] - 1e3*model.gen_disp[zone, gen_tech, time]
              for zone in model.zones_per_region[region]
              for gen_tech in model.commit_gen_tech_per_zone[zone]
              )\
        + sum(model.stor_reserve[zone, store_tech, time]
              for zone in model.zones_per_region[region]
              for store_tech in model.stor_tech_per_zone[zone]
              )\
        + sum(model.hyb_reserve[zone, hyb_tech, time]
              for zone in model.zones_per_region[region]
              for hyb_tech in model.hyb_tech_per_zone[zone]
              )\
        + sum(model.ev_reserve[zone, ev_tech, time]
              for zone in model.zones_per_region[region]
              for ev_tech in model.ev_tech_per_zone[zone]
              )\
        >= model.nem_disp_ratio * model.region_net_demand_less_evs[region, time]


def con_nem_re_disp_ratio(model, r, t):
    '''inequality constraint setting renewable dispatchable generation must be greater than
    disp_ratio * total generation, in each region and each hour'''
    return sum(model.gen_disp[z, n, t]
               for z in model.zones_per_region[r]
               for n in model.re_disp_gen_tech_per_zone[z]
               )\
        + sum(model.stor_disp[z, s, t]
              for z in model.zones_per_region[r]
              for s in model.stor_tech_per_zone[z]
              )\
        + sum(model.hyb_disp[z, h, t]
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              )\
        >= model.nem_re_disp_ratio * (sum(model.gen_disp[z, n, t]
                                          for z in model.zones_per_region[r]
                                          for n in model.gen_tech_per_zone[z]
                                          )
                                      + sum(model.stor_disp[z, s, t]
                                            for z in model.zones_per_region[r]
                                            for s in model.stor_tech_per_zone[z]
                                            )
                                      + sum(model.hyb_disp[z, h, t]
                                            for z in model.zones_per_region[r]
                                            for h in model.hyb_tech_per_zone[z]
                                            )
                                      )


def con_region_ret_ratio(model, r):
    '''inequality constraint setting renewable generation must be greater than
    ratio * total generation, in each region'''
    return sum(model.gen_disp[z, n, t]
               for z in model.zones_per_region[r]
               for n in model.re_gen_tech_per_zone[z]
               for t in model.t
               )\
        + sum(model.hyb_disp[z, h, t]
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              for t in model.t
              )\
        >= model.region_ret_ratio[r] * (
        sum(model.gen_disp[z, n, t]
            for z in model.zones_per_region[r]
            for n in model.gen_tech_per_zone[z]
            for t in model.t
            )
        + sum(model.hyb_disp[z, h, t]
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              for t in model.t
              )
    )


def con_max_mhw_per_zone(model, zone, tech):
    '''MWH maximum generation over a period for a tech in a zone.

       Results scaled to yearly MWH using year correction factor'''
    if cemo.const.DEFAULT_MAX_MWH_PER_ZONE.get(tech) is not None:
        return sum(model.gen_disp[zone, tech, time] for time in model.t)\
            <= 1e-3*cemo.const.DEFAULT_MAX_MWH_PER_ZONE.get(tech).get(zone, 0) /\
            model.year_correction_factor
    return Constraint.Skip


def con_max_cap_factor_per_zone(model, zone, tech):
    '''limit maximum generation as capacity factor over a period for a tech in a zone

    Results scaled to yearly capacity factor using year correction factor'''
    if cemo.const.DEFAULT_MAX_CAP_FACTOR_PER_ZONE.get(tech) is not None:
        return (sum(model.gen_disp[zone, tech, time] for time in model.t)
                <= 1e-3 * cemo.const.DEFAULT_MAX_CAP_FACTOR_PER_ZONE.get(tech).get(zone)
                * 8760 * model.gen_cap_op[zone, tech] / model.year_correction_factor)
    return Constraint.Skip


def con_max_mwh_nem_wide(model, tech):
    '''limit maximum generation over a period for a tech nem wide.

       Results scaled to yearly MWH using year correction factor'''
    if cemo.const.DEFAULT_MAX_MWH_NEM_WIDE.get(tech) is not None:
        return sum(model.gen_disp[zone, tech, time]
                   for zone in model.zones if tech in model.gen_tech_per_zone[zone]
                   for time in model.t)\
            <= 1e-3 * cemo.const.DEFAULT_MAX_MWH_NEM_WIDE.get(tech) /\
            model.year_correction_factor
    return Constraint.Skip


def con_max_trans(model, zone_source, zone_dest, time):
    '''constrain hourly transmission per link to be less than capacity
    It includes hard coded constraints for Murray/Tumit limitations on interconnectors'''
    if zone_source == 5 and zone_dest == 12:
        return 1e3*model.intercon_disp[zone_source, zone_dest, time] \
            <= model.intercon_cap_op[zone_source, zone_dest] \
            - (1350 - 400) / 2303 * 1e3*model.gen_disp[5, 18, time]
    if zone_source == 12 and zone_dest == 5:
        return 1e3*model.intercon_disp[zone_source, zone_dest, time] \
            <= model.intercon_cap_op[zone_source, zone_dest] \
            - (1600 - 700) / 2222 * 1e3*model.gen_disp[12, 18, time]
    return 1e3*model.intercon_disp[zone_source, zone_dest, time] \
        <= model.intercon_cap_op[zone_source, zone_dest]


def con_intercon_cap(model, zone_source, zone_dest):
    '''Operating transmission capacity is the net of
       - initial (or carryover)
       - model decisions
       -exogenous builds'''
    return model.intercon_cap_op[zone_source, zone_dest] \
        == model.intercon_cap_initial[zone_source, zone_dest]\
        + model.intercon_cap_exo[zone_source, zone_dest]\
        + model.intercon_cap_new[zone_source, zone_dest]\
        + model.intercon_cap_new[zone_dest, zone_source]


def con_stor_flow_lim(model, z, s, t):
    '''limit flow of charge/discharge to storage to be less than storage nameplate capacity'''
    return (model.stor_charge[z, s, t]
            + 1e3*model.stor_disp[z, s, t]
            + model.stor_reserve[z, s, t]) <= model.stor_cap_op[z, s]


def con_stor_reserve_lim(model, z, s, t):
    '''limit flow of energy out of storage to be less than its nameplate capacity'''
    return model.stor_reserve[z, s, t] <= model.stor_level[z, s, t]


def con_maxcharge(model, z, s, t):
    '''Storage charge must not exceed maximum capacity'''
    return model.stor_level[z, s, t] \
        <= model.stor_cap_op[z, s] * model.stor_charge_hours[s]


def con_storcharge(model, z, s, t):
    '''Storage charge dynamic'''
    return model.stor_level[z, s, t] \
        == model.stor_level[z, s, model.t.prevw(t)] \
        - 1e3*model.stor_disp[z, s, t] + \
        model.stor_rt_eff[s] * model.stor_charge[z, s, t]


def con_hybcharge(model, z, h, t):
    '''Hybrid charge dynamic'''
    return model.hyb_level[z, h, t] \
        == model.hyb_level[z, h, model.t.prevw(t)] \
        - 1e3*model.hyb_disp[z, h, t] \
        + model.hyb_charge[z, h, t]


def con_hyb_level_max(model, z, h, t):
    '''Hybrid storage charge is limted by collector output.

    '''
    return model.hyb_charge[z, h, t] \
        <= model.hyb_cap_factor[z, h, t] * model.hyb_col_mult[h] * model.hyb_cap_op[z, h]


def con_hyb_flow_lim(model, zone, hyb_tech, time):
    '''Hybrid storage charge/discharge flow is limited by plant capacity.

    In the case of CSP, storage can charge faster than power block'''
    return 1e3*model.hyb_disp[zone, hyb_tech, time] + model.hyb_reserve[zone, hyb_tech, time] \
        <= model.hyb_cap_op[zone, hyb_tech]


def con_hyb_reserve_lim(model, zone, hyb_tech, time):
    '''limit hybrid reserves to be within storage charge. '''
    return model.hyb_reserve[zone, hyb_tech, time] <= model.hyb_level[zone, hyb_tech, time]


def con_maxchargehy(model, z, h, t):
    '''Hybrid storage cannot charge beyond its maximum charge capacity'''
    return model.hyb_level[z, h, t] \
        <= model.hyb_cap_op[z, h] * model.hyb_charge_hours[h]


######################## EV Rules: KP_MODIFIED_180820 ######################
# RULE 1: Battery energy level at t
def con_evcharge(model, z, e, t):
    '''EV charge dynamic'''
    # print("con_evcharge: --- z: {}, e: {}, t: {}, v2g disp: {}, transport: {}, charge (total): {}, ev_level prev: {}".format(z, e, t, model.ev_v2g_disp[z, e, t], model.ev_disp_transport[z, e, t], model.ev_charge[z, e, t], model.ev_level[z, e, model.t.prevw(t)]))

    return model.ev_level[z, e, t] \
        == model.ev_level[z, e, model.t.prevw(t)] \
        - (model.ev_v2g_disp[z, e, t] / model.ev_rt_eff[e]) \
        - model.ev_disp_transport[z, e, t]\
        + (model.ev_charge[z, e, t] * model.ev_rt_eff[e]) #KP_MODIFIED_010920 added efficiency here - v2g below is max and doesn't include eff. More power will be taken from the battery to get the same output due to eff. so divided by (made bigger here). For charging - only a proportion of the charge will be delivered to the battery, so multiplied (smaller).

# RULE 2: Maximum storage level less than total installed capacity
def con_maxchargeev(model, z, e, t): # KP_MODIFIED 170920 such that the ev_level can't go below 20% of max batt cap either
    '''EV storage cannot charge beyond its maximum charge capacity or under the EV battery fleet floor'''
    return model.ev_level[z, e, t] <= model.ev_cap_op[z, e]

# RULE 2B: Minimum storage level
def con_minchargeev(model, z, e, t): # KP_MODIFIED 170920 such that the ev_level can't go below 20% of max batt cap either
    '''EV storage cannot charge beyond its maximum charge capacity or under the EV battery fleet floor'''
    return model.ev_level[z, e, t] >= model.ev_level_floor * model.ev_cap_op[z, e]

# RULE 3: Energy balance
def con_ev_flow_lim(model, zone, ev_tech, time):
    '''EV storage charge/discharge flow is limited by plant capacity.'''
    return model.ev_charge[zone, ev_tech, time] + model.ev_v2g_disp[zone, ev_tech, time] + model.ev_disp_transport[zone, ev_tech, time] + model.ev_reserve[zone, ev_tech, time] <= model.ev_cap_op[zone, ev_tech] #N.B. following suit for 1e3 from jose. wasn't in my intial
    #KP_MODIFIED_010920 to remove the 1e-3 and keep in mw

# RULE 4: Battery reserve to be less than charge level
def con_ev_reserve_lim(model, zone, ev_tech, time):
    '''limit ev reserves to be within storage charge. '''
    return model.ev_reserve[zone, ev_tech, time] <= model.ev_level[zone, ev_tech, time]

# RULE 5: Read in the transport energy requirement trace
def con_ev_trans_disp(model, z, e, t): # in MWh, hourly basis
    return model.ev_disp_transport[z, e, t] == model.ev_trans_trace[z,e, t]/1000  * model.ev_num_vehs[z, e]# / model.ev_rt_eff[e] #KP_MODIFIED_180820_2 #KP_MODIFIED_010920 to remove efficiency as already included in the traces program

# RULE 6: Calculate EV capacity
def con_ev_cap(model, z, e):
    '''Calculate EV capacity as the net of model and exogenous decisions'''
    return model.ev_cap_op[z, e] == model.ev_cap_initial[z, e] + model.ev_cap_exo[z, e]

# RULE 7: Set V2G level to 0 if V2G is off - absolute limit of v2g (max discharge rate * num veh * prop connected * prop willing to participate) -> efficiency ISN'T included here because this is the maximum the grid can provide. Need to include in the load balance for the battery.
def con_ev_v2g(model, z, e, t):
    if e in model.v2g_tech:
        return model.ev_v2g_disp[z, e, t] <= model.ev_connected[z,e, t] * model.ev_num_vehs[z,e] * model.ev_max_charge_rate[e] * model.percent_v2g_enabled #KP_MODIFIED_180820_2 / model.ev_rt_eff[e]
    else:
        return model.ev_v2g_disp[z, e, t] == 0

# RULE 9: Set dumb charging profile
#KP_MODIFIED 281020 TO LESS THAN OR EQUAL TO -> THIS IS THE MAXIMUM, DON'T NEED TO TAKE INTO CONSIDERATION SMART CHARGE TECH AS IT WILL OPTIMISE THAT AND THEN DO THIS.
def con_ev_dumb_charge(model, z, e, t): # in MWh, hourly basis #KP_MODIFIED_070920 to be in GWh and see if that works
    # if e in model.smart_charge_tech:
    return model.ev_dumb_charge[z, e, t] <= model.ev_charge_dumb_trace[z,e, t]/1000 * model.ev_num_vehs[z, e] #* (1-model.percent_smart_enabled)# / model.ev_rt_eff[e] #KP_MODIFIED_010920 to remove efficiency from dumb charging trace as its already included in the external program
        #KP_MODIFIED_180820_2 changed from model.ev_charge_dumb_trace[z, e, t] * model.ev_num_vehs[z, e] and created below rule to convert
    # else: #KP_MODIFIED_010920 to include no smart charging for freight
        # return model.ev_dumb_charge[z, e, t] == model.ev_charge_dumb_trace[z,e, t]/1000 * model.ev_num_vehs[z, e]# * (1-model.percent_smart_enabled)# / model.ev_rt_eff[e] #KP_MODIFIED_010920 to remove efficiency from dumb charging trace as its already included in the external program
        #KP_MODIFIED_180820_2 changed from model.ev_charge_dumb_trace[z, e, t] * model.ev_num_vehs[z, e] and created below rule to convert

# RULE 9.5: Set minimum dumb charging profile
def con_ev_dumb_charge_min(model, z, e, t): # in MWh, hourly basis #KP_MODIFIED_070920 to be in GWh and see if that works
    # if e in model.smart_charge_tech:
    return model.ev_dumb_charge[z, e, t] >= model.ev_charge_dumb_trace[z,e, t]/1000 * model.ev_num_vehs[z, e] * (1-model.percent_smart_enabled)

# RULE 10: Set smart charging profile - absolute limit of smart charging (max charge rate * num veh * prop connected * prop willing to participate) -> efficiency ISN'T included here because this is the maximum the grid can provide. Need to include in the load balance for the battery.
def con_ev_smart_charge(model,z,e,t):
    if e in model.smart_charge_tech:
        if model.v2g_enabled > 0:
            return model.ev_smart_charge[z,e,t] <= model.ev_num_vehs[z,e] * model.ev_connected[z,e, t] * model.ev_max_charge_rate[e] * model.percent_smart_enabled # / model.ev_rt_eff[e]
        elif model.smart_fit_method == 1: #FiT Charging
            return model.ev_smart_charge[z,e,t] <= model.ev_num_vehs[z,e] * model.ev_connected[z,e, t] * model.ev_max_charge_rate[e] * model.percent_smart_enabled # / model.ev_rt_eff[e]
        elif model.smart_fit_method == 0: #Yearly payment to participate
            return model.ev_smart_charge[z,e,t] <= model.ev_num_smart_part[z,e] * model.ev_connected[z,e, t] * model.ev_max_charge_rate[e] * model.percent_smart_enabled
    else: #KP_MODIFIED_010920 to include no smart charging for freight
        return model.ev_smart_charge[z,e,t] == 0

# RULE 11: Number of vehicles
def con_ev_num_vehicles(model,z,e): #KP_MODIFIED_010920 removed t for this rule
    return model.ev_num_vehs[z,e] == model.ev_cap_op[z, e] / model.ev_batt_size[e]

# RULE 13: Number of vehicles participating in smart charging program (yearly)
def con_ev_num_smart_participating_vehicles(model,z,e): #KP_MODIFIED_010920 removed t for this rule
    if model.smart_fit_method == 0:
        return model.ev_num_smart_part[z,e] <= model.ev_num_vehs[z,e] * model.percent_smart_enabled
    elif model.smart_fit_method == 1: #FiT Charging
        return model.ev_num_smart_part[z,e] == 0

# RULE 8: Set charging level to trace if dumb charging, and limit to amount of vehicles connected and the charge rate otherwise
def con_ev_level_max(model, z, e, t): #From the perspective of the grid - total dumb charging (already includes losses) and total smart - from grids perspective not cars.
    return model.ev_charge[z, e, t] == model.ev_dumb_charge[z, e, t] + model.ev_smart_charge[z,e,t]

#########################################################################

def con_ldbal(model, z, t):
    """Provides a rule defining a load balance constraint for the model"""
    return sum(1e3*model.gen_disp[z, n, t] for n in model.gen_tech_per_zone[z])\
        + sum(1e3*model.hyb_disp[z, h, t] for h in model.hyb_tech_per_zone[z])\
        + sum(model.ev_disp_transport[z, e, t] for e in model.ev_tech_per_zone[z])\
        + sum(model.ev_v2g_disp[z, e, t] for e in model.ev_tech_per_zone[z])\
        + sum(1e3*model.stor_disp[z, s, t] for s in model.stor_tech_per_zone[z])\
        + sum(1e3*model.intercon_disp[p, z, t] for p in model.intercon_per_zone[z])\
        + model.unserved[z, t]\
        == model.region_net_demand_less_evs[region_in_zone(z), t] * model.zone_demand_factor[z, t]\
        + sum((1.0 + model.intercon_loss_factor[z, p]) * 1e3*model.intercon_disp[z, p, t]
              for p in model.intercon_per_zone[z])\
        + sum(model.stor_charge[z, s, t] for s in model.stor_tech_per_zone[z])\
        + sum(model.ev_charge[z, e, t] for e in model.ev_tech_per_zone[z])\
        + model.surplus[z, t]


def con_maxcap(model, zone, tech):
    '''Prevent resulting operational capacity to exceed build limits'''
    return model.gen_cap_op[zone, tech] <= model.gen_build_limit[zone, tech]

#KP_ADDED
# def con_maxcap_region(model, zone, tech):
#     '''Prevent resulting operational capacity to exceed build limits'''
#     print("---REGION BUILD LIMITS---")
#     print(tech)
#     print(sum(model.gen_cap_op[zone, tech] for zone in model.gen_tech_per_zone[zone]))
#     print(model.gen_build_limit_region[region, tech])
#     print("-------------------------")
#     return sum(model.gen_cap_op[zone, tech] for zone in model.gen_tech_per_zone[zone]) <= model.gen_build_limit_region[region, tech]


def con_emissions(model):
    '''Emission constraint for the NEM in MT/y for total emissions'''
    return model.year_correction_factor * 1e-6*sum(
        emissions(model, region)
        for region in model.regions) <= 1e3 * model.nem_emit_limit


def build_adjust_exo_cap(model):
    '''Trim exogenous capacity decisions to a value that does not violate constraints.

    In the case of exogenous builds, that they do not violate build limits
    '''
    for zone, tech in model.gen_tech_in_zones:
        if value(model.gen_cap_initial[zone, tech]) > value(model.gen_build_limit[zone, tech]):
            model.gen_cap_initial[zone, tech] = value(model.gen_build_limit[zone, tech])
        if value(model.gen_cap_initial[zone, tech]
                 + model.gen_cap_exo[zone, tech]) > value(model.gen_build_limit[zone, tech]):
            model.gen_cap_exo[zone, tech] = value(
                model.gen_build_limit[zone, tech]-model.gen_cap_initial[zone, tech])


def build_adjust_exo_ret(model):
    '''Trim exogenous retirement decisions to a value that does not violate constraints.

    In the case of exogenous retires, that they do not retire beyond existing capacity.
    '''
    for zone, tech in model.retire_gen_tech_in_zones:
        if value(model.gen_cap_initial[zone, tech] - model.ret_gen_cap_exo[zone, tech]) < 0:
            model.ret_gen_cap_exo[zone, tech] = value(model.gen_cap_initial[zone, tech])


def con_gen_cap(model, z, n):  # z and n come both from TechinZones
    '''Calculate operating capacity as the net of model and exogenous decisions'''
    if n in model.nobuild_gen_tech:
        if n in model.retire_gen_tech:
            return model.gen_cap_op[z, n] == model.gen_cap_initial[z, n] \
                + model.gen_cap_exo[z, n]\
                - model.gen_cap_ret[z, n] - model.ret_gen_cap_exo[z, n]
        return model.gen_cap_op[z, n] == model.gen_cap_initial[z, n] \
            + model.gen_cap_exo[z, n]

    if n in model.retire_gen_tech:
        return model.gen_cap_op[z, n] == model.gen_cap_initial[z, n] \
            + model.gen_cap_exo[z, n]\
            + model.gen_cap_new[z, n]\
            - model.gen_cap_ret[z, n] - model.ret_gen_cap_exo[z, n]
    return model.gen_cap_op[z, n] == model.gen_cap_initial[z, n]\
        + model.gen_cap_exo[z, n]\
        + model.gen_cap_new[z, n]


def con_stor_cap(model, z, s):  # z and n come both from TechinZones
    '''Calculate Storage capacity as the net of model and exogenous decisions'''
    if s in model.nobuild_gen_tech:
        return model.stor_cap_op[z, s] == model.stor_cap_initial[z, s] \
            + model.stor_cap_exo[z, s]
    return model.stor_cap_op[z, s] == model.stor_cap_initial[z, s]\
        + model.stor_cap_exo[z, s]\
        + model.stor_cap_new[z, s]


def con_hyb_cap(model, z, h):  # z and n come both from TechinZones
    '''Calculate Hybrid capacity as the net of model and exogenous decisions'''
    if h in model.nobuild_gen_tech:
        return model.hyb_cap_op[z, h] == model.hyb_cap_initial[z, h] \
            + model.hyb_cap_exo[z, h]
    return model.hyb_cap_op[z, h] == model.hyb_cap_initial[z, h]\
        + model.hyb_cap_exo[z, h]\
        + model.hyb_cap_new[z, h]


def con_caplim(model, z, n, t):  # z and n come both from TechinZones
    '''Dispatch within the hourly limit on capacity factor for operating capacity'''
    if cemo.const.GEN_COMMIT['penalty'].get(n) is not None:
        return 1e3*model.gen_disp_com[
            z, n, t] <= model.gen_cap_factor[z, n, t] * model.gen_cap_op[z, n]
    return 1e3*model.gen_disp[z, n, t] \
        <= model.gen_cap_factor[z, n, t] * model.gen_cap_op[z, n]


def con_min_load_commit(model, z, n, t):
    '''Dispatch at least min % pct of committed capacity'''
    mincap = cemo.const.GEN_COMMIT['mincap'].get(n)
    return model.gen_disp[z, n, t] >= mincap * model.gen_disp_com[z, n, t]


def con_disp_ramp_down(model, z, n, t):
    '''dispatch less than ramp down commitment'''
    ramp_dn = cemo.const.GEN_COMMIT['rate down'].get(n)
    return model.gen_disp[z, n, t] <= model.gen_disp_com[z, n, t] +\
        (ramp_dn - 1) * model.gen_disp_com_m[z, n, model.t.nextw(t)]


def con_disp_ramp_up(model, z, n, t):
    '''dispatch less than ramp up commitment'''
    ramp_up = cemo.const.GEN_COMMIT['rate up'].get(n)
    return model.gen_disp[z, n, t] <= model.gen_disp_com[z, n, model.t.prevw(t)] + \
        ramp_up * model.gen_disp_com_p[z, n, t]


def con_ramp_down_uptime(model, z, n, t):
    '''commitment ramp down must respect up - time minimum'''
    return model.gen_disp_com_m[z, n, t] <= model.gen_disp_com_s[z, n, t]


def con_uptime_commitment(model, z, n, t):
    '''capacity that can be switched off, observing up - time'''
    uptime = cemo.const.GEN_COMMIT['uptime'].get(n)
    return model.gen_disp_com_s[z, n, t] == model.gen_disp_com_s[z, n, model.t.prevw(t)] +\
        model.gen_disp_com_p[z, n, model.t.prevw(
            t, k=uptime)] - model.gen_disp_com_m[z, n, t]


def con_committed_cap(model, z, n, t):
    '''Committed capacity for each time step'''
    return model.gen_disp_com[z, n, t] == model.gen_disp_com[z, n, model.t.prevw(t)] -\
        model.gen_disp_com_m[z, n, t] + \
        model.gen_disp_com_p[z, n, model.t.prevw(t)]


def con_uns(model, r):
    '''constraint limiting unserved energy'''
    return sum(model.unserved[z, t] for z in model.zones_per_region[r] for t in model.t) \
        <= 0.00002 * sum(model.region_net_demand_less_evs[r, t] for t in model.t)


def cost_repayment(model):
    '''calculate repayment costs per zone'''
    return sum(model.cost_cap_carry_forward[zone] for zone in model.zones)


def cost_capital(model):
    '''calculate total build costs'''
    return sum(cost_build_per_zone_model(model, zone)
               + cost_build_per_zone_exo(model, zone) for zone in model.zones)


def cost_capital_model(model):
    '''calculate total endogenous build costs'''
    return sum(cost_build_per_zone_model(model, zone) for zone in model.zones)


def cost_build_per_zone_model(model, zone):
    '''calculate endogenous build costs per zone'''
    return sum(model.cost_gen_build[zone, tech]
               * (model.gen_cap_new[zone, tech])
               * model.fixed_charge_rate[tech]
               for tech in model.gen_tech_per_zone[zone])\
        + sum(model.cost_stor_build[zone, tech]
              * (model.stor_cap_new[zone, tech])
              * model.fixed_charge_rate[tech]
              for tech in model.stor_tech_per_zone[zone])\
        + sum(model.cost_hyb_build[zone, tech]
              * (model.hyb_cap_new[zone, tech])
              * model.fixed_charge_rate[tech]
              for tech in model.hyb_tech_per_zone[zone])


def cost_build_per_zone_exo(model, zone):
    '''calculate exogenous build costs per zone'''
    return sum(model.cost_gen_build[zone, tech]
               * (model.gen_cap_exo[zone, tech])
               * model.fixed_charge_rate[tech]
               for tech in model.gen_tech_per_zone[zone])\
        + sum(model.cost_stor_build[zone, tech]
              * (model.stor_cap_exo[zone, tech])
              * model.fixed_charge_rate[tech]
              for tech in model.stor_tech_per_zone[zone])\
        + sum(model.cost_hyb_build[zone, tech]
              * (model.hyb_cap_exo[zone, tech])
              * model.fixed_charge_rate[tech]
              for tech in model.hyb_tech_per_zone[zone])


def cost_trans_build(model):
    '''Add total build costs for transmission upgrades'''
    return sum(cost_trans_build_per_zone_model(model, zone)
               + cost_trans_build_per_zone_exo(model, zone) for zone in model.zones)


def cost_trans_build_model(model):
    '''Add build costs for endogenous transmission upgrades'''
    return sum(cost_trans_build_per_zone_model(model, zone) for zone in model.zones)


def cost_trans_build_per_zone_model(model, zone):
    '''Tally endogenous transmission build costs from a zone'''
    return sum(model.cost_intercon_build[zone, dest]
               * (model.intercon_cap_new[zone, dest])
               * model.intercon_fixed_charge_rate
               for dest in model.intercon_per_zone[zone])


def cost_trans_build_per_zone_exo(model, zone):
    '''Tally exogenous transmission build costs from a zone'''
    return sum(model.cost_intercon_build[zone, dest]
               * (model.intercon_cap_exo[zone, dest])
               * model.intercon_fixed_charge_rate
               for dest in model.intercon_per_zone[zone])


def cost_retirement(model):
    '''Calculate total retirment costs for all retired capacity'''
    return sum(model.cost_retire[n]
               * (model.gen_cap_ret[z, n] + model.ret_gen_cap_exo[z, n])
               for z in model.zones for n in model.retire_gen_tech_per_zone[z])


def cost_retirement_model(model):
    '''Calculate Endogenous retirment costs for all retired capacity'''
    return sum(model.cost_retire[n]
               * (model.gen_cap_ret[z, n])
               for z in model.zones for n in model.retire_gen_tech_per_zone[z])


def cost_fixed(model):
    ''' calculate FOM costs'''
    return sum(model.cost_gen_fom[n] * model.gen_cap_op[z, n]
               for z in model.zones
               for n in model.gen_tech_per_zone[z])\
        + sum(model.cost_stor_fom[s] * model.stor_cap_op[z, s]
              for z in model.zones
              for s in model.stor_tech_per_zone[z])\
        + sum(model.cost_ev_fom[e] * model.ev_cap_op[z, e]
              for z in model.zones
              for e in model.ev_tech_per_zone[z])\
        + sum(model.cost_hyb_fom[h] * model.hyb_cap_op[z, h]
              for z in model.zones
              for h in model.hyb_tech_per_zone[z])


def cost_unserved(model):
    '''Calculate yearly adjusted USE costs'''
    return model.year_correction_factor * model.cost_unserved * sum(model.unserved[z, t]
                                                                    for z in model.zones
                                                                    for t in model.t)


def cost_operating(model):
    '''Calculate Variable operating costs.

    VOM costs are the sum of:
    - generator VOM costs
    - flexible generator fuel costs
    - non-flexible generator fuel costs
    - non-flexible generator start up fuel costs
    - storage VOM costs
    - Hybrid COM costs
    '''
    return model.year_correction_factor * (
        sum(model.cost_gen_vom[n] * 1e3*model.gen_disp[z, n, t]
            for z in model.zones for n in model.gen_tech_per_zone[z]
            for t in model.t)
        + sum(model.cost_fuel[z, f] * model.fuel_heat_rate[z, f]
              * 1e3*model.gen_disp[z, f, t] for z in model.zones
              for f in set(model.fuel_gen_tech_per_zone[z]) - set(model.commit_gen_tech_per_zone[z])
              for t in model.t)
        + sum(cost_fuel_non_flexible(model, z, f, t) for z in model.zones
              for f in model.commit_gen_tech_per_zone[z]
              for t in model.t)
        + sum(model.cost_fuel[z, n] * cemo.const.GEN_COMMIT['penalty'].get(n, 0)
              * 1e3*model.gen_disp_com_p[z, n, t]
              for z in model.zones
              for n in model.commit_gen_tech_per_zone[z]
              for t in model.t)
        + sum(model.cost_stor_vom[s] * 1e3*model.stor_disp[z, s, t]
              for z in model.zones for s in model.stor_tech_per_zone[z]
              for t in model.t)
        + sum(model.cost_hyb_vom[h] * 1e3*model.hyb_disp[z, h, t]
              for z in model.zones
              for h in model.hyb_tech_per_zone[z] for t in model.t)
        )

def cost_v2g_payments(model):
    return model.year_correction_factor * (
        sum(model.cost_ev_vom[e] * model.ev_v2g_disp[z, e, t]
              for z in model.zones
              for e in model.ev_tech_per_zone[z] for t in model.t)
        )

def cost_smart_payments(model):
    if model.percent_v2g_enabled > 0:
        return 0
    else:
        if model.smart_fit_method == 0: #yearly one off payment to each vehicle owner
            # print("Yearly one off payments")
            # No need to multiply by year correction factor as this is a one off payment for the year
            return (sum(model.cost_ev_smart_vom[e] * model.ev_num_smart_part[z,e]
                      for z in model.zones
                      for e in model.ev_tech_per_zone[z])
                )
        elif model.smart_fit_method == 1:#FiT per kWh smart charged
            # print("Smart FiT Payments")
            return model.year_correction_factor * (
                sum(model.cost_ev_smart_vom[e] * model.ev_smart_charge[z, e, t]
                      for z in model.zones
                      for e in model.ev_tech_per_zone[z] for t in model.t)
                )


def cost_fuel_non_flexible(model, zone, tech, time):
    '''Fuel cost for non flexible generators.

    Heat rate varies linearly to simulate lower efficiency at part load'''
    mincap = cemo.const.GEN_COMMIT['mincap'].get(tech)
    effrate = cemo.const.GEN_COMMIT['effrate'].get(tech)
    return model.cost_fuel[zone, tech] * (
        mincap * 1e3*model.gen_disp_com[zone, tech, time]
        * model.fuel_heat_rate[zone, tech] / effrate
        + (1e3*model.gen_disp[zone, tech, time] - mincap
           * 1e3*model.gen_disp_com[zone, tech, time]) * model.fuel_heat_rate[zone, tech]
        * (1 - mincap / effrate) / (1 - mincap))


def cost_trans_flow(model):
    '''Calculate transmission flow costs'''
    return model.year_correction_factor * model.cost_trans * sum(
        1e3*model.intercon_disp[zone, dest, time] for zone in model.zones
        for dest in model.intercon_per_zone[zone] for time in model.t)


def cost_emissions(model):
    '''Calculate emission costs from all fuel based generators
    times their respective emissions rate'''
    return model.year_correction_factor * model.cost_emit * sum(
        emissions(model, r) for r in model.regions)


def cost_shadow(model):
    '''Calculate shadow costs, i.e. penalties applied to
    ensure numerical stability of model'''
    return model.year_correction_factor * (model.cost_unserved + 10) * sum(model.surplus[z, t]
                                                                           for z in model.zones
                                                                           for t in model.t)


def system_cost(model):
    """Total cost of system"""
    return cost_capital(model) + cost_repayment(model)\
        + cost_fixed(model) + cost_unserved(model) + cost_operating(model)\
        + cost_trans_build(model) + cost_trans_flow(model) + cost_emissions(model)\
        + cost_retirement(model) + cost_v2g_payments(model) + cost_smart_payments(model)


def obj_cost(model):
    """Model optimisation objective"""
    return (cost_capital_model(model)
            + cost_fixed(model) + cost_unserved(model) + cost_operating(model)
            + cost_trans_build_model(model)
            + cost_trans_flow(model) + cost_emissions(model) + cost_v2g_payments(model) + cost_smart_payments(model)
            + cost_retirement_model(model) + cost_shadow(model)) / model.year_correction_factor
