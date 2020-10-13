"""openCEM model structure"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"

from collections import namedtuple
from pyomo.environ import (AbstractModel, BuildAction, Constraint, Expression,
                           NonNegativeReals, Objective, Param, Set, Suffix,
                           Var)
import cemo.const
from cemo.initialisers import (init_cap_factor, init_cost_retire,
                               init_default_capex,
                               init_default_fuel_emit_rate,
                               init_default_fuel_price, init_default_heat_rate,
                               init_default_lifetime, init_fcr,
                               init_gen_build_limit, init_gen_build_limit_region, init_hyb_charge_hours,
                               init_hyb_col_mult, init_intercon_build_cost,
                               init_ev_rt_eff,
                               init_ev_charge_rate,  init_ev_batt_size, init_ev_trans_trace,
                               init_intercon_cap_initial, init_intercon_fcr,
                               init_intercon_loss_factor,
                               init_intercons_in_zones, init_stor_charge_hours,
                               init_stor_rt_eff, init_year_correction_factor,
                               init_zone_demand_factors, init_zones_in_regions)
from cemo.rules import (ScanForHybridperZone, ScanForEVperZone, ScanForStorageperZone,
                        ScanForTechperZone, ScanForZoneperRegion,
                        build_intercon_per_zone, build_carry_fwd_cost_per_zone,
                        build_adjust_exo_cap, build_adjust_exo_ret, build_cap_factor_thres,
                        con_caplim, con_max_cap_factor_per_zone,
                        con_committed_cap, con_disp_ramp_down, con_disp_ramp_up, con_emissions,
                        con_gen_cap, con_hyb_cap, con_hyb_flow_lim,
                        con_hyb_level_max, con_hyb_reserve_lim, con_hybcharge,
                        con_ev_cap, con_evcharge, con_maxchargeev, con_minchargeev, con_ev_flow_lim, con_ev_trans_disp,
                        con_ev_reserve_lim, con_ev_v2g, con_ev_level_max, con_ev_num_vehicles,
                        con_intercon_cap, con_ldbal, con_max_mhw_per_zone,
                        con_max_mwh_nem_wide, con_max_trans, con_maxcap,
                        con_maxcharge, con_maxchargehy, con_min_load_commit,
                        con_operating_reserve, con_nem_re_disp_ratio,
                        con_nem_ret_gwh, con_nem_ret_ratio,
                        con_ramp_down_uptime, con_region_ret_ratio,
                        con_stor_cap,
                        con_stor_flow_lim, con_stor_reserve_lim,
                        con_storcharge, con_uns, con_uptime_commitment,
                        obj_cost, con_ev_dumb_charge, con_ev_smart_charge)


def model_options(**kwargs):
    '''Container for model options'''
    FIELDS = {'unslim': False,
              'nem_emit_limit': False,
              'nem_ret_ratio': False,
              'nem_ret_gwh': False,
              'region_ret_ratio': False,
              'nem_disp_ratio': True,
              'v2g_enabled': False,
              'smart_enabled': False,
              'ev_level_floor_soc': False,
              'nem_re_disp_ratio': False,
              'build_intercon_manual': False}
    opt = namedtuple('model_options', [i for i in FIELDS])
    opt.__new__.__defaults__ = tuple(FIELDS[i] for i in FIELDS)
    return opt(**kwargs)


class CreateModel():
    def __init__(self, namestr, model_options):
        self.m = AbstractModel(name=namestr)
        self.model_options = model_options

    def create_sets(self):
        # Sets
        # Set of NEM regions
        self.m.regions = Set(initialize=cemo.const.REGION.keys())
        self.m.zones = Set(
            initialize=cemo.const.ZONE.keys())  # Set of NTNDP planning zones
        self.m.all_tech = Set(
            initialize=cemo.const.ALL_TECH)  # Set of generation technologies
        # set of fuel based gen technologies
        self.m.fuel_gen_tech = Set(
            initialize=cemo.const.FUEL_TECH) & self.m.all_tech
        # set of gen techs that obey linearised unit commitment constraints
        self.m.commit_gen_tech = Set(
            initialize=cemo.const.COMMIT_TECH) & self.m.all_tech
        # set of retireable technologies
        self.m.retire_gen_tech = Set(
            initialize=cemo.const.RETIRE_TECH) & self.m.all_tech
        # set of retireable technologies
        self.m.nobuild_gen_tech = Set(
            initialize=cemo.const.NOBUILD_TECH) & self.m.all_tech
        # Set of storage technologies
        self.m.stor_tech = Set(
            initialize=cemo.const.STOR_TECH) & self.m.all_tech
        # set of hybrid (gen+storage) technologies
        self.m.hyb_tech = Set(initialize=cemo.const.HYB_TECH) & self.m.all_tech
        self.m.ev_tech = Set(initialize=cemo.const.EV_TECH) & self.m.all_tech

        # Set of dispatch intervals
        self.m.t = Set(ordered=True)

        # Sparse set of zones per region
        self.m.zones_in_regions = Set(
            dimen=2, initialize=init_zones_in_regions)
        # Set listing technologies avaialable per zone (like a sparsity pattern)
        self.m.gen_tech_in_zones = Set(dimen=2)
        # Set listing technologies avaialable per region (like a sparsity pattern)
        self.m.gen_tech_in_regions = Set(dimen=2)
        # Retirable technologies avaialable per zone (like a sparsity pattern)
        self.m.retire_gen_tech_in_zones = Set(dimen=2)
        # Fuel/emmitting technologies avaialable per zone (like a sparsity pattern)
        self.m.fuel_gen_tech_in_zones = Set(dimen=2)
        # Fuel/emmitting technologies avaialable per zone (like a sparsity pattern)
        self.m.commit_gen_tech_in_zones = Set(dimen=2)
        # Renewable technologies avaialable per zone (like a sparsity pattern)
        self.m.re_gen_tech_in_zones = Set(dimen=2)
        # Dispatchable technologies avaialable per zone (like a sparsity pattern)
        self.m.disp_gen_tech_in_zones = Set(dimen=2)
        # Renewable Dispatchable technologies avaialable per zone (like a sparsity pattern)
        self.m.re_disp_gen_tech_in_zones = Set(dimen=2)
        # Set listing storage avaialable per zone (like a sparsity pattern)
        self.m.hyb_tech_in_zones = Set(dimen=2)
        # Set listing ev avaialable per zone (like a sparsity pattern) #KP_ADDED
        self.m.ev_tech_in_zones = Set(dimen=2)
        # Set listing storage avaialable per zone (like a sparsity pattern)
        self.m.stor_tech_in_zones = Set(dimen=2)
        # Set listing transmission lines to other regions in each region
        self.m.intercons_in_zones = Set(
            dimen=2, initialize=init_intercons_in_zones)

        # sparse sets built by build actions
        # Returns a list of planning zones for each region in R
        self.m.zones_per_region = Set(
            self.m.regions, within=self.m.zones, initialize=[])
        # Returns a tuple with generating techs in each zone
        self.m.gen_tech_per_zone = Set(
            self.m.zones, within=self.m.all_tech, initialize=[])
        # Returns a tuple with emitting techs in each zone
        self.m.fuel_gen_tech_per_zone = Set(
            self.m.zones, within=self.m.all_tech, initialize=[])
        # tuple for techs that obey linearised unit commitment constraints
        self.m.commit_gen_tech_per_zone = Set(
            self.m.zones, within=self.m.all_tech, initialize=[])
        self.m.re_gen_tech_per_zone = Set(
            self.m.zones, within=self.m.all_tech, initialize=[])
        self.m.disp_gen_tech_per_zone = Set(
            self.m.zones, within=self.m.all_tech, initialize=[])
        self.m.re_disp_gen_tech_per_zone = Set(
            self.m.zones, within=self.m.all_tech, initialize=[])
        # Returns a tuple with retirable techs in each zone
        self.m.retire_gen_tech_per_zone = Set(
            self.m.zones, within=self.m.all_tech, initialize=[])
        # Returns a tuple with storage techs in each zone
        self.m.stor_tech_per_zone = Set(
            self.m.zones, within=self.m.stor_tech, initialize=[])
        # Returns a tuple with emitting techs in each zone
        self.m.hyb_tech_per_zone = Set(
            self.m.zones, within=self.m.all_tech, initialize=[])
        # Returns a tuple with emitting techs in each zone
        self.m.ev_tech_per_zone = Set(
            self.m.zones, within=self.m.all_tech, initialize=[])
        # returns a tuple with transmission links in each region
        self.m.intercon_per_zone = Set(self.m.zones, initialize=[])

        self.m.smart_charge_tech = Set(initialize=cemo.const.SMART_CHARGE_EV_TECH) & self.m.all_tech
        # set of ev tech WITHOUT V2G enabled
        self.m.v2g_tech = Set(initialize=cemo.const.V2G_EV_TECH) & self.m.all_tech


        # @@ Build actions
        # Scan TechinZones and populate ?_gen_tech_per_zone
        self.m.TpZ_build = BuildAction(rule=ScanForTechperZone)
        # Scan HybTechinZones and populate hyb_tech_per_zone
        self.m.HpZ_build = BuildAction(rule=ScanForHybridperZone)
        # Scan EVTechinZones and populate ev_tech_per_zone
        self.m.EpZ_build = BuildAction(rule=ScanForEVperZone)
        # Scan ZinR and populate ZperR
        self.m.ZpR_build = BuildAction(rule=ScanForZoneperRegion)
        # Scan TransLines and populate intercon_per_zone
        self.m.intercon_build = BuildAction(rule=build_intercon_per_zone)
        # Scan StorinZones and populate stor_tech_per_zone
        self.m.SpZ_build = BuildAction(rule=ScanForStorageperZone)

    def create_params(self):
        # @@ Parameters
        # Capital costs generators
        # Build costs for generators
        self.m.cost_gen_build = Param(
            self.m.gen_tech_in_zones, initialize=init_default_capex)
        self.m.cost_stor_build = Param(
            self.m.stor_tech_in_zones)  # Capital costs storage
        self.m.cost_hyb_build = Param(
            self.m.hyb_tech_in_zones)  # Capital costs hybrid
        self.m.cost_ev_build = Param(
            self.m.ev_tech_in_zones) #,  initialize=init_default_capex)
        # Capital costs $/MW/km trans
        self.m.cost_intercon_build = Param(
            self.m.intercons_in_zones, initialize=init_intercon_build_cost)

        self.m.cost_fuel = Param(
            self.m.fuel_gen_tech_in_zones,
            initialize=init_default_fuel_price)  # Fuel cost

        # Fixed operating costs generators
        self.m.cost_gen_fom = Param(self.m.all_tech)
        # Variable operating costs generators
        self.m.cost_gen_vom = Param(self.m.all_tech)
        # Fixed operating costs storage
        self.m.cost_stor_fom = Param(self.m.stor_tech)
        # Variable operating costs storage
        self.m.cost_stor_vom = Param(self.m.stor_tech)
        # Fixed operating costs hybrid
        self.m.cost_hyb_fom = Param(self.m.hyb_tech)
        # Variable operating costs hybrid
        self.m.cost_hyb_vom = Param(self.m.hyb_tech)

        # Fixed operating costs ev
        self.m.cost_ev_fom = Param(self.m.ev_tech)
        # Variable operating costs ev
        self.m.cost_ev_vom = Param(self.m.ev_tech)

        # Technology lifetime in years
        self.m.all_tech_lifetime = Param(
            self.m.all_tech, initialize=init_default_lifetime)
        # Project discount rate
        self.m.all_tech_discount_rate = Param(default=0.05)
        # % Fleet V2G EV Discharging enabled
        self.m.percent_v2g_enabled = Param(default=0)
        # % Fleet Smart EV Charging enabled
        self.m.percent_smart_enabled = Param(default=0.5)
        # EV Fleet Batt Level Floor
        self.m.ev_level_floor = Param(default=0.2)

        # Generator tech fixed charge rate
        self.m.fixed_charge_rate = Param(self.m.all_tech, initialize=init_fcr)
        # Transmission tech fixed charge rate
        self.m.intercon_fixed_charge_rate = Param(initialize=init_intercon_fcr)
        # Per year cost adjustment for sims shorter than 1 year of dispatch
        self.m.year_correction_factor = Param(
            initialize=init_year_correction_factor)

        self.m.cost_retire = Param(
            self.m.retire_gen_tech, initialize=init_cost_retire)
        self.m.cost_unserved = Param(
            initialize=cemo.const.
            DEFAULT_COSTS["unserved"])  # cost of unserved power
        # cost in $/kg of total emissions
        self.m.cost_emit = Param(initialize=cemo.const.DEFAULT_COSTS["emit"])
        self.m.cost_trans = Param(
            initialize=cemo.const.DEFAULT_COSTS["trans"])  # cost of transmission

        # Round trip efficiency of storage technology
        self.m.stor_rt_eff = Param(
            self.m.stor_tech, initialize=init_stor_rt_eff)
        # Number of hours of storage technology
        self.m.stor_charge_hours = Param(
            self.m.stor_tech, initialize=init_stor_charge_hours)

        # Round trip efficiency of ev technology
        self.m.ev_rt_eff = Param(self.m.ev_tech, initialize=init_ev_rt_eff)
        self.m.ev_connected =  Param(self.m.ev_tech_in_zones, self.m.t, default=0) #KP_MODIFIED_180820_2 from  ev_tech_in_zones #KP_MODIFIED_030920 changed back to ev_tech_in_zones from ev_tech
        # Max charge rate & v2g discharge rate
        self.m.ev_max_charge_rate = Param(self.m.ev_tech, initialize=init_ev_charge_rate)
        # Battery size per vehicle
        self.m.ev_batt_size = Param(self.m.ev_tech, initialize=init_ev_batt_size)
        self.m.ev_trans_trace = Param(self.m.ev_tech_in_zones, self.m.t, default=0)  # Trnasport energy trace read in #KP_MODIFIED_180820_2 from self.m.ev_tech_in_zones  #KP_MODIFIED_030920 changed back to ev_tech_in_zones from ev_tech
        self.m.ev_charge_dumb_trace = Param(self.m.ev_tech_in_zones,  self.m.t, default=0)


        # Collector multiple of hybrid technology
        self.m.hyb_col_mult = Param(
            self.m.hyb_tech, initialize=init_hyb_col_mult)
        # Number of hours of storage technology
        self.m.hyb_charge_hours = Param(
            self.m.hyb_tech, initialize=init_hyb_charge_hours)

        self.m.fuel_heat_rate = Param(
            self.m.fuel_gen_tech_in_zones, initialize=init_default_heat_rate)
        # Emission rates
        self.m.fuel_emit_rate = Param(
            self.m.fuel_gen_tech, initialize=init_default_fuel_emit_rate)
        # proportioning factors for notional interconnectors
        self.m.intercon_loss_factor = Param(
            self.m.intercons_in_zones, initialize=init_intercon_loss_factor)

        self.m.gen_cap_factor = Param(
            self.m.gen_tech_in_zones, self.m.t,
            initialize=init_cap_factor, mutable=True)  # Capacity factors for generators
        self.m.hyb_cap_factor = Param(
            self.m.hyb_tech_in_zones, self.m.t,
            initialize=init_cap_factor, mutable=True)  # Capacity factors for generators
        self.m.ev_cap_factor = Param(
            self.m.ev_tech_in_zones, self.m.t,
            initialize=init_cap_factor, mutable=True)
        # Revise cap factors for numbers below threshold of 1e-5
        self.m.build_cap_factor_thres = BuildAction(rule=build_cap_factor_thres)

        # Maximum capacity per generating technology per zone
        self.m.gen_build_limit = Param(
            self.m.gen_tech_in_zones, initialize=init_gen_build_limit)
        self.m.gen_build_limit_region = Param(
            self.m.gen_tech_in_zones, initialize=init_gen_build_limit_region)
        self.m.gen_cap_initial = Param(
            self.m.gen_tech_in_zones, default=0, mutable=True)  # operating capacity
        self.m.stor_cap_initial = Param(
            self.m.stor_tech_in_zones, default=0)  # operating capacity
        self.m.hyb_cap_initial = Param(
            self.m.hyb_tech_in_zones, default=0)  # operating capacity
        self.m.ev_cap_initial = Param(
            self.m.ev_tech_in_zones, default=0)
        self.m.intercon_cap_initial = Param(
            self.m.intercons_in_zones, initialize=init_intercon_cap_initial)  # operating capacity
        # exogenous new capacity
        self.m.gen_cap_exo = Param(self.m.gen_tech_in_zones, default=0, mutable=True)
        # exogenous new storage capacity
        self.m.stor_cap_exo = Param(self.m.stor_tech_in_zones, default=0)
        # exogenous new hybrid capacity
        self.m.hyb_cap_exo = Param(self.m.hyb_tech_in_zones, default=0)
        self.m.ev_cap_exo = Param(self.m.ev_tech_in_zones, default=0)

        # exogenous transmission capacity
        self.m.intercon_cap_exo = Param(self.m.intercons_in_zones, default=0)
        self.m.ret_gen_cap_exo = Param(
            self.m.retire_gen_tech_in_zones, default=0, mutable=True)
        # Net Electrical load (may include rooftop and EV)
        self.m.region_net_demand = Param(self.m.regions, self.m.t)
        self.m.region_net_demand_less_evs = Param(self.m.regions, self.m.t) #Removing the EV demand (AEMO assumed) for each year

        # AEMO EV Demand trace
        self.m.aemo_ev = Param(self.m.regions, self.m.t)

        # Zone load distribution factors as a pct of region demand
        self.m.zone_demand_factor = Param(
            self.m.zones, self.m.t, initialize=init_zone_demand_factors)
        # carry forward capital costs calculated
        self.m.cost_cap_carry_forward_sim = Param(self.m.zones, default=0)
        # carry forward capital costs NEM historical estimate
        self.m.cost_cap_carry_forward_hist = Param(self.m.zones, default=0)
        # carry forward capital costs total
        self.m.cost_cap_carry_forward = Param(self.m.zones, mutable=True)

        # Build action to Compute carry forward costs
        self.m.cost_carry_forward_build = BuildAction(
            rule=build_carry_fwd_cost_per_zone)
        # Create params for model options
        for option in self.model_options._fields:
            if getattr(self.model_options, option):
                if cemo.const.DEFAULT_MODEL_OPT.get(option, {}).get("index", None) is None:
                    setattr(self.m,
                            option,
                            Param(default=cemo.const.DEFAULT_MODEL_OPT.get(option, {}).get('value', 0))
                            )
                else:
                    setattr(self.m,
                            option,
                            Param(eval(cemo.const.DEFAULT_MODEL_OPT[option].get("index", None)),
                                  default=cemo.const.DEFAULT_MODEL_OPT.get(option, {}).get('value', 0))
                            )
        # Build action to prevent exogenous buids to exceed build limits
        self.m.build_adjust_exo_cap = BuildAction(rule=build_adjust_exo_cap)
        # Build action to prevent exogenous retires to make capacity negative
        self.m.build_adjust_exo_ret = BuildAction(rule=build_adjust_exo_ret)

    def create_vars(self):
        # @@ Variables
        # New capacity
        self.m.gen_cap_new = Var(
            self.m.gen_tech_in_zones, within=NonNegativeReals, bounds=cemo.const.CAP_BOUNDS)
        self.m.gen_cap_op = Var(
            self.m.gen_tech_in_zones,
            within=NonNegativeReals, bounds=cemo.const.CAP_BOUNDS)  # Total generation capacity
        # New storage capacity
        self.m.stor_cap_new = Var(
            self.m.stor_tech_in_zones, within=NonNegativeReals, bounds=cemo.const.CAP_BOUNDS)
        self.m.stor_cap_op = Var(
            self.m.stor_tech_in_zones,
            within=NonNegativeReals, bounds=cemo.const.CAP_BOUNDS)  # Total storage capacity
        self.m.hyb_cap_new = Var(
            self.m.hyb_tech_in_zones, within=NonNegativeReals, bounds=cemo.const.CAP_BOUNDS)
        self.m.hyb_cap_op = Var(self.m.hyb_tech_in_zones,
                                within=NonNegativeReals, bounds=cemo.const.CAP_BOUNDS)
        self.m.ev_cap_op = Var(self.m.ev_tech_in_zones, within=NonNegativeReals)

        intercon_bounds = None #cemo.const.CAP_BOUNDS
        if self.model_options.build_intercon_manual:
            intercon_bounds = (0, 0)

        self.m.intercon_cap_new = Var(
            self.m.intercons_in_zones, within=NonNegativeReals, bounds=intercon_bounds)
        self.m.intercon_cap_op = Var(
            self.m.intercons_in_zones, within=NonNegativeReals) #, bounds=cemo.const.CAP_BOUNDS)
        self.m.gen_cap_ret = Var(
            self.m.retire_gen_tech_in_zones,
            within=NonNegativeReals) #, bounds=cemo.const.CAP_BOUNDS)  # retireable capacity
        # dispatched power
        self.m.gen_disp = Var(
            self.m.gen_tech_in_zones,
            self.m.t, within=NonNegativeReals) #, bounds=cemo.const.SCALED_DISP_BOUNDS)
        # Variables for committed power constraints
        self.m.gen_disp_com = Var(
            self.m.commit_gen_tech_in_zones,
            self.m.t, within=NonNegativeReals) #, bounds=cemo.const.SCALED_DISP_BOUNDS)
        self.m.gen_disp_com_p = Var(
            self.m.commit_gen_tech_in_zones,
            self.m.t, within=NonNegativeReals) #, bounds=cemo.const.SCALED_DISP_BOUNDS)
        self.m.gen_disp_com_m = Var(
            self.m.commit_gen_tech_in_zones,
            self.m.t, within=NonNegativeReals) #, bounds=cemo.const.SCALED_DISP_BOUNDS)
        self.m.gen_disp_com_s = Var(
            self.m.commit_gen_tech_in_zones,
            self.m.t, within=NonNegativeReals) #, bounds=cemo.const.SCALED_DISP_BOUNDS)

        self.m.stor_disp = Var(
            self.m.stor_tech_in_zones, self.m.t,
            within=NonNegativeReals) #, bounds=cemo.const.SCALED_DISP_BOUNDS)  # dispatch from storage
        self.m.stor_reserve = Var(
            self.m.stor_tech_in_zones, self.m.t,
            within=NonNegativeReals) #, bounds=cemo.const.DISP_BOUNDS)  # dispatched power from storage
        self.m.stor_charge = Var(
            self.m.stor_tech_in_zones, self.m.t,
            within=NonNegativeReals) #, bounds=cemo.const.DISP_BOUNDS)  # power to charge storage

        self.m.hyb_disp = Var(
            self.m.hyb_tech_in_zones, self.m.t,
            within=NonNegativeReals) #, bounds=cemo.const.SCALED_DISP_BOUNDS)  # dispatch from hybrid

        self.m.hyb_reserve = Var(
            self.m.hyb_tech_in_zones, self.m.t,
            within=NonNegativeReals) #, bounds=cemo.const.DISP_BOUNDS)  # reserve capacity for hybrids

        self.m.hyb_charge = Var(
            self.m.hyb_tech_in_zones, self.m.t,
            within=NonNegativeReals) #, bounds=cemo.const.DISP_BOUNDS)  # charging power from hybrid

        self.m.stor_level = Var(
            self.m.stor_tech_in_zones, self.m.t,
            within=NonNegativeReals) #, bounds=cemo.const.STOR_BOUNDS)  # Charge level for storage

        self.m.hyb_level = Var(
            self.m.hyb_tech_in_zones, self.m.t,
            within=NonNegativeReals) #, bounds=cemo.const.STOR_BOUNDS)  # Charge level for storage

        self.m.ev_reserve = Var(self.m.ev_tech_in_zones, self.m.t, within=NonNegativeReals)  # reserve capacity for ev  #KP_ADDED
        self.m.ev_level = Var(self.m.ev_tech_in_zones, self.m.t, within=NonNegativeReals)  # Charge level for ev
        self.m.ev_charge = Var(self.m.ev_tech_in_zones, self.m.t, within=NonNegativeReals)  # charging power from ev  #KP_ADDED
        self.m.ev_v2g_disp = Var(self.m.ev_tech_in_zones, self.m.t, within=NonNegativeReals)  # dispatched power from ev via V2G #KP_ADDED
        self.m.ev_disp_transport = Var(self.m.ev_tech_in_zones, self.m.t, within=NonNegativeReals) # dispatched power from ev from transport
        self.m.ev_dumb_charge = Var(self.m.ev_tech_in_zones,  self.m.t, within=NonNegativeReals) #KP_MODIFIED
        self.m.ev_smart_charge = Var(self.m.ev_tech_in_zones,  self.m.t, within=NonNegativeReals) #KP_MODIFIED
        self.m.ev_num_vehs = Var(self.m.ev_tech_in_zones, within=NonNegativeReals) #number of installed vehicles



        # Numerical relaxation to load balance and capacity decisions
        self.m.unserved = Var(self.m.zones, self.m.t,
                              within=NonNegativeReals) #, bounds=cemo.const.DISP_BOUNDS)
        self.m.surplus = Var(self.m.zones, self.m.t,
                             within=NonNegativeReals) #, bounds=cemo.const.DISP_BOUNDS)

        # Interconnector flow
        self.m.intercon_disp = Var(
            self.m.intercons_in_zones,
            self.m.t, within=NonNegativeReals) #,            bounds=cemo.const.SCALED_DISP_BOUNDS)

    def create_constraints(self):
        # @@ Constraints
        # Transmission limits
        self.m.con_max_trans = Constraint(
            self.m.intercons_in_zones, self.m.t, rule=con_max_trans)
        # Transmission capacity balance
        self.m.con_intercon_cap = Constraint(
            self.m.intercons_in_zones, rule=con_intercon_cap)
        # Load balance
        self.m.ldbal = Constraint(self.m.zones, self.m.t, rule=con_ldbal)
        # Dispatch to be within capacity, RE have variable capacity factors
        self.m.caplim = Constraint(
            self.m.gen_tech_in_zones, self.m.t, rule=con_caplim)
        # Limit maximum capacity to be built in each region and each technology
        self.m.maxcap = Constraint(self.m.gen_tech_in_zones, rule=con_maxcap)
        # gen_cap_op in existing period is previous gen_cap_op plus gen_cap_new
        self.m.con_gen_cap = Constraint(
            self.m.gen_tech_in_zones, rule=con_gen_cap)
        # MaxMWh limit
        self.m.con_max_mwh_per_zone = Constraint(
            self.m.gen_tech_in_zones, rule=con_max_mhw_per_zone)
        # MaxMWh limit as capacity factor
        self.m.con_max_cap_factor_per_zone = Constraint(
            self.m.gen_tech_in_zones, rule=con_max_cap_factor_per_zone)
        # MaxMWh limit (currently only for BIOMASS)
        self.m.con_max_mwh_nem_wide = Constraint(
            self.m.all_tech, rule=con_max_mwh_nem_wide)
        # linearised unit commitment constraints
        self.m.con_min_load_commit = Constraint(
            self.m.commit_gen_tech_in_zones, self.m.t, rule=con_min_load_commit)
        self.m.con_disp_ramp_down = Constraint(
            self.m.commit_gen_tech_in_zones, self.m.t, rule=con_disp_ramp_down)
        self.m.con_disp_ramp_up = Constraint(
            self.m.commit_gen_tech_in_zones, self.m.t, rule=con_disp_ramp_up)
        self.m.con_ramp_down_uptime = Constraint(
            self.m.commit_gen_tech_in_zones, self.m.t, rule=con_ramp_down_uptime)
        self.m.con_uptime_commitment = Constraint(
            self.m.commit_gen_tech_in_zones, self.m.t, rule=con_uptime_commitment)
        self.m.con_committed_cap = Constraint(
            self.m.commit_gen_tech_in_zones, self.m.t, rule=con_committed_cap)
        # NEM operating reserve constraint
        self.m.con_operating_reserve = Constraint(
            self.m.regions, self.m.t, rule=con_operating_reserve)
        # Hard constraint on unserved energy
        if self.model_options.unslim:
            self.m.con_uns = Constraint(self.m.regions, rule=con_uns)
        # Emmissions constraint
        if self.model_options.nem_emit_limit:
            self.m.con_emissions = Constraint(rule=con_emissions)
            # NEM wide RET constraint as a ratio
        if self.model_options.nem_ret_ratio:
            # NEM wide renewable energy constraint
            self.m.con_nem_ret_ratio = Constraint(rule=con_nem_ret_ratio)
        # NEM wide RET constraint as a ratio
        if self.model_options.nem_ret_gwh:
            # NEM wide renewable energy constraint
            self.m.con_nem_ret_gwh = Constraint(rule=con_nem_ret_gwh)

        if self.model_options.region_ret_ratio:
            # Regional RET constraint
            self.m.con_region_ret = Constraint(
                self.m.regions, rule=con_region_ret_ratio)
        if self.model_options.nem_re_disp_ratio:
            # NEM wide minimum hourly dispatch from dispatchable sources constraint
            self.m.con_nem_re_disp_ratio = Constraint(
                self.m.regions, self.m.t, rule=con_nem_re_disp_ratio)

        # Storage charge/discharge dynamic
        self.m.StCharDis = Constraint(
            self.m.stor_tech_in_zones, self.m.t, rule=con_storcharge)
        # Maxiumum rate of storage charge
        self.m.con_stor_flow_lim = Constraint(
            self.m.stor_tech_in_zones, self.m.t, rule=con_stor_flow_lim)
        # Maxiumum rate of storage discharge
        self.m.con_stor_reserve_lim = Constraint(
            self.m.stor_tech_in_zones, self.m.t, rule=con_stor_reserve_lim)
        # Maxiumum charge capacity of storage
        self.m.MaxCharge = Constraint(
            self.m.stor_tech_in_zones, self.m.t, rule=con_maxcharge)
        # StCap in existing period is previous stor_cap_op plus stor_cap_new
        self.m.con_stor_cap = Constraint(
            self.m.stor_tech_in_zones, rule=con_stor_cap)

        # Hybrid charge/discharge dynamic
        self.m.HybCharDis = Constraint(
            self.m.hyb_tech_in_zones, self.m.t, rule=con_hybcharge)
        # Maxiumum level of hybrid storage discharge
        self.m.con_hyb_level_max = Constraint(
            self.m.hyb_tech_in_zones, self.m.t, rule=con_hyb_level_max)
        # Maxiumum rate of hybrid storage charge/discharge
        self.m.con_hyb_flow_lim = Constraint(
            self.m.hyb_tech_in_zones, self.m.t, rule=con_hyb_flow_lim)
        # Limit hybrid reserve capacity to be within storage level
        self.m.con_hyb_reserve_lim = Constraint(
            self.m.hyb_tech_in_zones, self.m.t, rule=con_hyb_reserve_lim)
        # Maxiumum charge capacity of storage
        self.m.MaxChargehy = Constraint(
            self.m.hyb_tech_in_zones, self.m.t, rule=con_maxchargehy)
        # HyCap in existing period is previous stor_cap_op plus stor_cap_new
        self.m.con_hyb_cap = Constraint(
            self.m.hyb_tech_in_zones, rule=con_hyb_cap)

        ####################### EV RULES #KP_MODIFIED_180820 ##################
        # RULE 6 - CALCULATE EV CAPACITY # EVCap in existing period is previous stor_cap_op plus stor_cap_new
        self.m.con_ev_cap = Constraint(self.m.ev_tech_in_zones, rule=con_ev_cap)
        # RULE 11 - NUMBER OF VEHICLES INSTALLED
        self.m.con_ev_num_vehicles = Constraint(self.m.ev_tech_in_zones, rule=con_ev_num_vehicles)
        # RULE 5 - TRANSPORT
        self.m.con_ev_trans_disp = Constraint(self.m.ev_tech_in_zones, self.m.t, rule=con_ev_trans_disp)
        # RULE 9 - DUMB CHARGING
        self.m.con_ev_dumb_charge = Constraint(self.m.ev_tech_in_zones, self.m.t, rule=con_ev_dumb_charge)
        # RULE 10 - SMART CHARGING
        self.m.con_ev_smart_charge = Constraint(self.m.ev_tech_in_zones, self.m.t, rule=con_ev_smart_charge)
        # RULE 7 - V2G DISPATCHED
        self.m.con_ev_v2g = Constraint(self.m.ev_tech_in_zones, self.m.t, rule=con_ev_v2g)
        #RULE 1 - BATTERY LEVEL # EV charge/discharge dynamic
        self.m.EVCharDis = Constraint(self.m.ev_tech_in_zones, self.m.t, rule=con_evcharge)
        # RULE 8 - CHARGING LEVEL # Total EV charging
        self.m.con_ev_level_max = Constraint(self.m.ev_tech_in_zones, self.m.t, rule=con_ev_level_max)
        # RULE 2 - MAX. STORAGE LEVEL # Maxiumum charge capacity of storage
        self.m.MaxChargeev = Constraint(self.m.ev_tech_in_zones, self.m.t, rule=con_maxchargeev)
        # RULE 2B - MIN. STORAGE LEVEL # Minimum charge capacity of storage
        self.m.MinChargeev = Constraint(self.m.ev_tech_in_zones, self.m.t, rule=con_minchargeev)
        # RULE 3 - ENERGY BALANCE # Maxiumum rate of ev storage charge/discharge
        self.m.con_ev_flow_lim = Constraint(self.m.ev_tech_in_zones, self.m.t, rule=con_ev_flow_lim)
        # RULE 4 - BATTERY RESERVE LIMIT # Limit ev reserve capacity to be within storage level
        self.m.con_ev_reserve_lim = Constraint(self.m.ev_tech_in_zones, self.m.t, rule=con_ev_reserve_lim)


        ############################################################
    def create_objective(self):
        # @@ Objective
        # Minimise capital, variable and fixed costs of system
        self.m.FSCost = Expression(expr=0)
        self.m.SSCost = Expression(rule=obj_cost)
        # objective: minimise all other objectives
        self.m.Obj = Objective(expr=self.m.FSCost + self.m.SSCost)

        # Short run marginal prices
        self.m.dual = Suffix(direction=Suffix.IMPORT)

    def create_model(self, test=False):
        """Creates an instance of the pyomo definition of openCEM"""
        self.create_sets()
        self.create_params()
        if test:
            return self.m
        self.create_vars()
        self.create_constraints()
        self.create_objective()
        return self.m
