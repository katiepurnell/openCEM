"""Constants module for openCEM"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"

REGION = {1: 'NSW', 2: 'QLD', 3: 'SA', 4: 'TAS', 5: 'VIC'}

TECH_TYPE = {
    1: 'biomass', # N.B. no initial generators in ISP2020 (was 385MW in 2018...). N.B. no costing available in this version either - replaced by tech 34 - don't include
    2: 'ccgt', # N.B. no capex for this - nobuild tech -> new costs are in the new tech type 36
    3: 'ccgt_ccs', # N.B. no capex for this - nobuild tech
    4: 'coal_sc', # N.B. no capex for this - nobuild tech
    5: 'coal_sc_ccs', # N.B. no capex for this - nobuild tech
    6: 'brown_coal_sc', # N.B. no capex for this - nobuild tech
    7: 'brown_coal_sc_ccs', # N.B. no capex for this - nobuild tech
    8: 'ocgt', # N.B. no capex for this - nobuild tech
    9: 'solar_pv_dat', # Dual-axis tracking # N.B. no capex for this - nobuild tech
    10: 'solar_pv_ffp', # Fixed flat PV # N.B. no capex for this - nobuild tech
    11: 'solar_pv_sat', # Single-axis tracking # N.B. no capex costings for z4 or 14 ( SEQ & ADE ) - maybe its the size / population density?
    12: 'wind', # N.B. no capex costings for z4 or 14 ( SEQ & ADE ) - maybe its the size / population density?
    13: 'cst_6h', # N.B. no capex costings for z4 or 14 ( SEQ & ADE ) - maybe its the size / population density?
    14: 'phes_6h',
    15: 'battery_2h',
    16: 'recip_engine', # N.B. no capex for this - nobuild tech. For ISP2020 only initially in z13 & 14
    17: 'wind_h', # N.B. no capex costings for z4 or 14 ( SEQ & ADE ) - maybe its the size / population density?
    18: 'hydro', # N.B. no capex for this - nobuild tech
    19: 'gas_thermal', # N.B. no capex for this - nobuild tech
    20: 'pumps', # N.B. no capex for this - nobuild tech and no opex either -> no initial capacity either - do not include
    21: 'phes_168h', #SNOWY2.0 # N.B. no capex for this - nobuild tech and no opex either -> no initial capacity either - costings are from the exo file I believe. Z5
    22: 'cst_3h', # N.B. no capex for this - nobuild tech and no opex either -> no initial capacity either - in exo file
    23: 'cst_12h', # N.B. no capex for this - nobuild tech and no opex either -> no initial capacity either - in exo file
    24: 'phes_3h', # N.B. no capex for this - nobuild tech and no opex either -> no initial capacity either - in exo file
    25: 'phes_12h',
    26: 'battery_1h',# N.B. no capex for this - nobuild tech and no opex either -> no initial capacity either - in exo file
    27: 'battery_3h', # N.B. no capex for this - nobuild tech and no opex either -> no initial capacity either - in exo file
    28: 'coal_sc_new', # No capex for z9 (LV lower VIC)
    29: 'brown_coal_sc_new', # N.B. costings only available for z9 (VIC) which makes sense
    30: 'wind_offshore', # N.B. no costings for z4 or 14 ( SEQ & ADE ) - unsure why
    31: 'phes_24h', # N.B. available for all zones
    32: 'phes_48h', # N.B. available for all zones
    33: 'battery_4h', # N.B. available for all zones
    34: 'biomass_new', # N.B. available for all zones
    35: 'ocgt_new', # N.B. available for all zones
    36: 'ccgt_new', # N.B. available for all zones
    50: 'private_cars',
    51: 'light_commercial_vehicles',
    52: 'taxis',
    53: 'bicycles',
    60: 'public buses',
    61: 'ferries',
    70: 'road freight',
}

ZONE = {
    1: 'NQ',
    2: 'CQ',
    3: 'SWQ',
    4: 'SEQ',
    5: 'SWNSW',
    6: 'CAN',
    7: 'NCEN',
    8: 'NNS',
    9: 'LV',
    10: 'MEL',
    11: 'CVIC',
    12: 'NVIC',
    13: 'NSA',
    14: 'ADE',
    15: 'SESA',
    16: 'TAS'
}

ZONES_IN_REGIONS = [
    (1, 5),
    (1, 6),
    (1, 7),
    (1, 8),
    (2, 1),
    (2, 2),
    (2, 3),
    (2, 4),
    (3, 13),
    (3, 14),
    (3, 15),
    (4, 16),
    (5, 9),
    (5, 10),
    (5, 11),
    (5, 12),
]

# Source Modelling Transmission Frameworks Review (EPR0019) Roam Consulting,
# Table 4.4, 2029-2030 values, adapted to openCEM zones
ZONE_DEMAND_PCT = {
    1: {
        'peak': 0.08,
        'off peak': 0.18,
        'prov': 'QLD'
    },
    2: {
        'peak': 0.19,
        'off peak': 0.31,
        'prov': 'QLD'
    },
    3: {
        'peak': 0.16,
        'off peak': 0.15,
        'prov': 'QLD'
    },
    4: {
        'peak': 0.57,
        'off peak': 0.36,
        'prov': 'QLD'
    },
    5: {
        'peak': 0.05,
        'off peak': 0.07,
        'prov': 'NSW'
    },
    6: {
        'peak': 0.06,
        'off peak': 0.05,
        'prov': 'ACT'
    },
    7: {
        'peak': 0.83,
        'off peak': 0.84,
        'prov': 'NSW'
    },
    8: {
        'peak': 0.06,
        'off peak': 0.04,
        'prov': 'NSW'
    },
    9: {
        'peak': 0.05,
        'off peak': 0.06,
        'prov': 'VIC'

    },
    10: {
        'peak': 0.82,
        'off peak': 0.81,
        'prov': 'VIC'
    },
    11: {
        'peak': 0.08,
        'off peak': 0.07,
        'prov': 'VIC'
    },
    12: {
        'peak': 0.05,
        'off peak': 0.06,
        'prov': 'VIC'
    },
    13: {
        'peak': 0.36,
        'off peak': 0.55,
        'prov': 'SA'
    },
    14: {
        'peak': 0.59,
        'off peak': 0.39,
        'prov': 'SA'
    },
    15: {
        'peak': 0.05,
        'off peak': 0.06,
        'prov': 'SA'
    },
    16: {
        'peak': 1.0,
        'off peak': 1.0,
        'prov': 'TAS'
    }
}

ZONE_INTERCONS = {
    1: {
        2: {'loss': 0.02, 'limit': 1501, 'length': 600, 'buildcost': 2500}
    },
    2: {
        1: {'loss': 0.02, 'limit': 1501, 'length': 600, 'buildcost': 2500},
        3: {'loss': 0.02, 'limit': 1313, 'length': 385, 'buildcost': 2500},
        4: {'loss': 0.02, 'limit': 1421, 'length': 500, 'buildcost': 2500}
    },
    3: {
        2: {'loss': 0.02, 'limit': 1313, 'length': 385, 'buildcost': 2500},
        4: {'loss': 0.02, 'limit': 5288, 'length': 130, 'buildcost': 2500},
        8: {'loss': 0.02, 'limit': 1078, 'length': 415, 'buildcost': 2500},
    },
    4: {
        2: {'loss': 0.02, 'limit': 1421, 'length': 500, 'buildcost': 2500},
        3: {'loss': 0.02, 'limit': 5288, 'length': 130, 'buildcost': 2500},
        8: {'loss': 0.02, 'limit': 234, 'length': 375, 'buildcost': 2500},
    },
    5: {
        6: {'loss': 0.02, 'limit': 2022, 'length': 85, 'buildcost': 2500},
        # Estimated thermal limit based on 265MVAR capacity
        # Artificial length is 150 so that builds are more comparable
        11: {'loss': 0.2, 'limit': 200, 'length': 150, 'buildcost': 2500},
        12: {'loss': 0.2, 'limit': 1350, 'length': 150, 'buildcost': 2500},
        13: {'loss': 0.02, 'limit': 0, 'length': 600, 'buildcost': 2500},
    },
    6: {
        5: {'loss': 0.02, 'limit': 2022, 'length': 85, 'buildcost': 2500},
        7: {'loss': 0.02, 'limit': 2304, 'length': 115, 'buildcost': 2500},
    },
    7: {
        6: {'loss': 0.02, 'limit': 2304, 'length': 115, 'buildcost': 2500},
        8: {'loss': 0.02, 'limit': 929, 'length': 220, 'buildcost': 2500},
    },
    8: {
        3: {'loss': 0.61, 'limit': 486, 'length': 415, 'buildcost': 2500},
        4: {'loss': 0.61, 'limit': 105, 'length': 375, 'buildcost': 2500},
        7: {'loss': 0.02, 'limit': 929, 'length': 220, 'buildcost': 2500},
    },
    9: {
        10: {'loss': 0.02, 'limit': 8907, 'length': 136, 'buildcost': 2500},
        16: {'loss': 0.5, 'limit': 469, 'length': 320, 'buildcost': 2500},
    },
    10: {
        9: {'loss': 0.02, 'limit': 8907, 'length': 136, 'buildcost': 2500},
        11: {'loss': 0.02, 'limit': 542, 'length': 450, 'buildcost': 2500},
        12: {'loss': 0.02, 'limit': 1422, 'length': 216, 'buildcost': 2500},
        15: {'loss': 0.5, 'limit': 460, 'length': 125, 'buildcost': 2500},
        16: {'loss': 0.5, 'limit': 0, 'length': 320, 'buildcost': 2500},  # West Tas to Geelong
    },
    11: {
        # Estimated thermal limit based on 265MVAR capacity
        5: {'loss': 0.02, 'limit': 200, 'length': 20, 'buildcost': 2500},
        10: {'loss': 0.02, 'limit': 542, 'length': 450, 'buildcost': 2500},
        12: {'loss': 0.02, 'limit': 284, 'length': 490, 'buildcost': 2500},
        13: {'loss': 0.5, 'limit': 220, 'length': 150, 'buildcost': 2500},
    },
    12: {
        5: {'loss': 0.02, 'limit': 1600, 'length': 150, 'buildcost': 2500},
        10: {'loss': 0.02, 'limit': 1422, 'length': 216, 'buildcost': 2500},
        11: {'loss': 0.02, 'limit': 284, 'length': 490, 'buildcost': 2500},
    },
    13: {
        5: {'loss': 0.02, 'limit': 0, 'length': 600, 'buildcost': 2500},
        11: {'loss': 0.02, 'limit': 220, 'length': 150, 'buildcost': 2500},
        14: {'loss': 0.02, 'limit': 537, 'length': 100, 'buildcost': 2500},
    },
    14: {
        13: {'loss': 0.02, 'limit': 537, 'length': 100, 'buildcost': 2500},
        15: {'loss': 0.02, 'limit': 547, 'length': 380, 'buildcost': 2500},
    },
    15: {
        10: {'loss': 0.02, 'limit': 460, 'length': 125, 'buildcost': 2500},
        14: {'loss': 0.02, 'limit': 547, 'length': 380, 'buildcost': 2500},
    },
    16: {
        9: {'loss': 0.02, 'limit': 594, 'length': 320, 'buildcost': 2500},
        10: {'loss': 0.02, 'limit': 0, 'length': 320, 'buildcost': 2500},
        # Estimate based on ISP 2018 VIC-TAS option
    }
}

DEFAULT_CAPEX = {
    16: 1588176,  # GHD estimates for AEMO based on Barker Inlet
    21: 2549019.607  # 2040MW for $AUD 5.2 Billion
}

DEFAULT_FUEL_PRICE = {
    1: 0.5,
    2: 9.68,
    3: 9.68,
    4: 3.8,
    5: 3.8,
    6: 3.8,
    7: 3.8,
    8: 9.68,
    16: 9.68,
    19: 9.68,
    28: 3.5,
    29: 0.62,
    34: 0.59,
    35: 11.9,
    36: 9.68
}

DEFAULT_HEAT_RATE = {
    1: 12.66,
    2: 6.93,
    3: 7.93,
    4: 9.66,
    5: 11.52,
    6: 12.4,
    7: 17.4,
    8: 10.15,
    16: 7.6,
    19: 10.7,
    28: 8.975, #8.66
    29: 11.337,
    34: 13.39,
    35: 7.57533,
    36: 11.7497
}
DEFAULT_FUEL_EMIT_RATE = {
    1: 57.13,
    2: 410.0,
    3: 432.5,  # NTNDP data, not used
    4: 950.0,
    5: 1150.0,  # NTNDP data, not used
    6: 1203.0, #1100
    7: 1683.0,  # NTNDP data, not used
    8: 602.0,
    16: 602.0,
    19: 705.0,
    28: 821.0, #840
    29: 963.87,
    34: 57.13,
    35: 716.37,
    36: 459.0,
}

DEFAULT_MAX_CAP_FACTOR_PER_ZONE = {  # tech->zone
    1: {1: 0.8998, 2: 0.8998, 3: 0.8998, 4: 0.8998, 5: 0.8998, 6: 0.8998, 7: 0.8998, 8: 0.8998,
        9: 0.8998, 10: 0.8998, 11: 0.8998, 12: 0.8998, 13: 0.8998, 14: 0.8998, 15: 0.8998,
        16: 0.8998,
        },
    6: {9: 0.8743},
    4: {1: 0.8998,
        2: 0.8998,
        3: 0.8998,
        4: 0.8998,
        7: 0.75, #0.8626
        8: 0.75, #0.8626
        },
    29: {9: 0.9},
    28: {1: 0.9,
         2: 0.9,
         3: 0.9,
         4: 0.9,
         7: 0.9,
         8: 0.9,
         },
    34: {1: 0.8998, 2: 0.8998, 3: 0.8998, 4: 0.8998, 5: 0.8998, 6: 0.8998, 7: 0.8998, 8: 0.8998,
         9: 0.8998, 10: 0.8998, 11: 0.8998, 12: 0.8998, 13: 0.8998, 14: 0.8998, 15: 0.8998,
         16: 0.8998,
         }
}


DEFAULT_MAX_MWH_PER_ZONE = {
    18: {
        1: 0, # 662262 # openNEM data shows the 2010-2017 yearly average is 662262
        3: 0,
        4: 662262, #0
        5:
        2326421,  # openNEM data shows the 2009-2018 yearly average is 2326421
        6: 0,
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        12:
        2747264,  # openNEM data shows the 2009-2018 yearly average to be 2747264
        14: 0,
        16: 9165993  # openNEM 2009-2018 LTA is 9165993
    }
}

DEFAULT_MAX_MWH_NEM_WIDE = {
    1: 10624e3,  # Source Near term potential for Biomass CEC BioEnergy RoadMap 2008
    34: 10624e3,  # Source Near term potential for Biomass CEC BioEnergy RoadMap 2008
}


DEFAULT_RETIREMENT_COST = {
    2: 132071,#10487.98,
    3: 45716.8,#10487.98,
    4: 162549, #52439.9,
    5: 162549, #52439.9,
    6: 162549, #83903.4,
    7: 162549, #83903.4,
    8: 45716.8,#5243.99,
    11: 21842.8, #20975.96,
    12: 10487.98,
    14: 109214,
    16: 52439.9,
    17: 10921,
    19: 52439.9,  # Copy of 16
    36: 10487.98
}

DEFAULT_TECH_LIFETIME = {  # Source GHD 2018 AEMO cost and technical parameter review data book
    1: 50.0,
    2: 30.0,
    3: 30,
    4: 50,
    5: 50,
    6: 50,
    7: 50,
    8: 30,
    11: 30,
    12: 30,
    13: 40,
    14: 50,
    15: 15,
    17: 30,
    18: 50,
    19: 50,
    20: 50,
    21: 50.0,
    22: 40,
    23: 40,
    24: 50,
    25: 50,
    26: 15,
    27: 15,
    28: 50,
    29: 50,
    30: 30,
    31: 50,
    32: 50,
    33: 15,
    34: 50,
    35: 30,
    36: 30,
    50: 11,
    51: 11,
    52: 11,
    53: 11,
    60: 11,
    61: 11,
    70: 11,

}

# Numbers are sum of ISP Build limits plus initial capacity as per capex table
DEFAULT_BUILD_LIMIT = {
    1: {
        11: 19400 + 1029, #11: 9250 + 1001,
        12: 18500 + 0, #12: 8350 + 0,
        17: 6300 + 224, #17: 2785 + 235,
    },
    2: {
        11: 17900 + 265, #11: 6000 + 170,
        12: 6300 + 0, #12: 2105,
        17: 2200 + 0, #17: 695,
    },
    3: {
        11: 7700 + 424, #11: 4000 + 135,
        12: 4200 + 0, #12: 2090 + 0,
        17: 1400 + 453, #17: 695 + 453,
    },
    4: {
        11: 0 + 142, #0 + 52.5,
        12: 0,
        17: 0,
    },
    5: {
        11: 13100 + 1240, #4000 + 3000 + 1000 + 29.9,
        12: 7800 + 0, #1870 + 1620 + 232.5 + 0,
        17: 2700 + 199,  #620 + 527.5 + 77.5 + 199,  #
    },
    6: {
        11: 0 + 10, #1000 + 0,
        12: 200 + 0, #1735 + 0,
        17: 100 + 641, #575 + 914,
    },
    7: {
        11: 7200 + 436, #6750 + 150,
        12: 2200 + 0, #2265 + 0,
        17: 800 + 220, #755 + 431,
    },
    8: {
        11: 10000 + 57, #5000 + 57,
        12: 5600 + 0, #2760 + 0,
        17: 1800 + 443, #900 + 270,
    },
    9: {
        11: 0,
        12: 1500 + 0, #105 + 0,
        17: 500 + 107, #35 + 445,
        30: 4000 + 0
    },
    10: {
        11: 0, #30,
        12: 2900 + 0, #1725 + 0,
        17: 1000 + 602, #570 + 1220,
    },
    11: {
        11: 400 + 668, #0 + 3000 + 822,
        12: 2100 + 0, #1185 + 1620 + 0,
        17: 700 + 2882, #395 + 527.5 + 1918,
    },
    12: {
        11: 3000 + 112, # 0 + 453,
        12: 1200, #0
        17: 400 + 58 #0
    },
    13: {
        11: 21900 + 284,  # All NSA + 1/2 of Riverland+ existing #10950 + 1000 + 330,
        12: 5700 + 0, #2770 + 232.5 + 0,
        17: 2100 + 1783, #915 + 77.5 + 1462,
    },
    14: {
        11: 600, #0
        12: 3400 + 0, #1820 + 0,
        17: 1200 + 35, #605 + 35,
    },
    15: {
        11: 100 + 108, #0
        12: 2400 + 0, #1355 + 0,
        17: 800 + 325, #455 + 484,
    },
    16: {
        11: 150, #0
        12: 7200 + 0, #3480 + 0,
        17: 2600 + 574, #1155 + 592,
    }
}

GEN_CAP_FACTOR = {
    9: 0,
    10: 0,
    11: 0,
    12: 0,
    17: 0,
    30: 0,
}

CAP_FACTOR_THRES = 1e-4

DEFAULT_STOR_PROPS = {
    14: {"rt_eff": 0.8, "charge_hours": 6},
    24: {"rt_eff": 0.8, "charge_hours": 3},
    25: {"rt_eff": 0.8, "charge_hours": 12},
    21: {"rt_eff": 0.8, "charge_hours": 168},
    15: {"rt_eff": 0.8, "charge_hours": 2},
    26: {"rt_eff": 0.8, "charge_hours": 1},
    27: {"rt_eff": 0.8, "charge_hours": 3},
    31: {"rt_eff": 0.8, "charge_hours": 24},
    32: {"rt_eff": 0.8, "charge_hours": 48},
    33: {"rt_eff": 0.8, "charge_hours": 4}
}

DEFAULT_HYB_PROPS = {
    13: {"col_mult": 2.5, "charge_hours": 8}, #6
    22: {"col_mult": 2.1, "charge_hours": 3},
    23: {"col_mult": 3.1, "charge_hours": 12},
}

DEFAULT_EV_PROPS = {
    50: {"rt_eff": 0.95, "charge_rate": 0.0072, "default_batt_size": 0.05}, #where batt size is in MWh and charge rate is in MW
    51: {"rt_eff": 0.95, "charge_rate": 0.022, "default_batt_size": 0.05}, #lcv
    52: {"rt_eff": 0.95, "charge_rate": 0.022, "default_batt_size": 0.08}, #taxi
    53: {"rt_eff": 0.95, "charge_rate": 0.0024, "default_batt_size": 0.002}, #bicycle
    60: {"rt_eff": 0.95, "charge_rate": 0.050, "default_batt_size": 0.3}, #bus
    61: {"rt_eff": 0.95, "charge_rate": 0.9, "default_batt_size": 0.5}, #ferry
    70: {"rt_eff": 0.95, "charge_rate": 0.022, "default_batt_size": 0.15}, #freight
}

DEFAULT_COSTS = {
    "unserved": 14700, #980000,
    "trans": 0.02339,  # AEMO 2018-2019 budget
    "emit": 0,
}

DEFAULT_MODEL_OPT = {
    "nem_disp_ratio": {"value": 0.075},
    "region_ret_ratio": {"index": 'self.m.regions'}
}


GEN_COMMIT = {
    "penalty": {  # Startup fuel cost in GJ/MWh
        2: 19,
        3: 19,
        4: 41,
        5: 41,
        6: 41,
        7: 41,
        19: 25,
        28: 41,
        29: 41,
        36: 19,
    },
    "rate up": {
        2: 0.68,
        3: 0.68,
        4: 0.45,
        5: 0.45,
        6: 0.67,
        7: 0.67,
        19: 0.67,
        28: 0.45,
        29: 0.67,
        36: 0.68,
    },
    "rate down": {
        2: 0.87,
        3: 0.87,
        4: 0.41,
        5: 0.41,
        6: 0.67,
        7: 0.67,
        19: 0.67,
        28: 0.41,
        29: 0.67,
        36: 0.87,
    },
    "uptime": {
        2: 5, #4,
        3: 5, #4,
        4: 8, #12,
        5: 8, #12,
        6: 16, #12,
        7: 16, #12,
        19: 4, #12,
        28: 8, #12
        29: 16,
        36: 5
    },
    "mincap": {
        2: 0.5,
        3: 0.5,
        4: 0.5,
        5: 0.5,
        6: 0.5,
        7: 0.5,
        19: 0.5,
        28: 0.5,
        29: 0.5,
        36: 0.5
    },
    "effrate": {
        2: 0.85,
        3: 0.85,
        4: 0.85,
        5: 0.85,
        6: 0.85,
        7: 0.85,
        19: 0.85,
        28: 0.85,
        29: 0.85,
        36: 0.85
    }
}

ALL_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
            12, 13, 14, 15, 16, 17, 18, 19, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]

DISPLAY_ORDER =  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 29, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 50,51,52,53,60,61,70]
GEN_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18, 19, 20, 28, 29, 30, 34, 35, 36]
RE_GEN_TECH = [1, 9, 10, 11, 12, 17, 18, 30, 34]
DISP_GEN_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 16, 18, 19, 28, 29, 34, 35, 36]
RE_DISP_GEN_TECH = [1, 18, 34]
TRACE_TECH = [11, 12, 13, 17, 30]
FUEL_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 16, 19, 28, 29, 34, 35, 36]
COMMIT_TECH = [2, 3, 4, 5, 6, 7, 19, 28, 29, 36]
HYB_TECH = [13, 22, 23]
STOR_TECH = [14, 15, 21, 24, 25, 31, 32, 26, 27, 33]




RETIRE_TECH = [2, 3, 4, 5, 6, 7, 8, 16, 19]
NOBUILD_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 18, 19, 21]  # 3, 5 and 7 no build due to incomplete data #KP_MODIFIED to include 10 (solar pv ffp) because its not listed in the capex db
SYNC_TECH = [1, 2, 3, 4, 5, 6, 7, 8, 13, 15, 16, 18, 19, 34, 36]

EV_TECH = [50,51,52,53,60,61,70]
SMART_CHARGE_EV_TECH = [50,51,52,53,60,61,70]  # if included, means the solver will optimise the charging profile for that technology (for the proportion adopted) and read in the dumb charging profile for the rest. Not for freight.
V2G_EV_TECH = [50,51,52,53,60,61] # if included, means the solver will optimise the v2g discharge for that technology (for the proportion adopted) and set as 0 for the rest. Not for freight.


# Variable bounds for numerical solver performance
# Intended to inform solver of magnitude of varables, not to limit solution values
# Select smallest value that will not limit solutions
# Avoid using conservatively large values may negate the effect of speeding up solution
CAP_BOUNDS = (0, 2.5e5)  # maximum capacity per zone
DISP_BOUNDS = (0, 2.5e5)  # maximum dispatch per zone
SCALED_DISP_BOUNDS = (0, 3e1)  # maximum scaled dispatch per zone
STOR_BOUNDS = (0, 7.5e5)  # maximum storage level per zone


PALETTE = {
    1: (161 / 255, 135 / 255, 111 / 255, 1),  # biomass
    2: (251 / 255, 177 / 255, 98 / 255, 1),  # ccgt
    3: (251 / 255, 177 / 255, 98 / 255, 0.75),  # ccgt_sc
    4: (25 / 255, 25 / 255, 25 / 255, 1),  # coal_sc
    5: (25 / 255, 25 / 255, 25 / 255, 0.75),  # coal_sc_scc
    6: (137 / 255, 87 / 255, 45 / 255, 1),  # brown_coal_sc
    7: (137 / 255, 87 / 255, 45 / 255, 0.75),  # brown_coal_sc_scc
    8: (253 / 255, 203 / 255, 148 / 255, 1),  # ocgt
    9: (220 / 255, 205 / 255, 0, 0.6),  # PV DAT
    10: (220 / 255, 205 / 255, 0 / 255, 0.8),  # PV fixed
    11: (220 / 255, 205 / 255, 0 / 255, 1),  # PV SAT
    12: (67 / 255, 116 / 255, 14 / 255, 1),  # Wind
    13: (1, 209 / 255, 26 / 255, 1),  # CST 6h
    14: (137 / 255, 174 / 255, 207 / 255, 1),  # PHES 6 h
    15: (43 / 255, 161 / 255, 250 / 255, 1),  # Battery
    16: (240 / 255, 79 / 255, 35 / 255, 1),  # recip engine,
    17: (70 / 255, 120 / 255, 1, 1),  # Wind high
    18: (75 / 255, 130 / 255, 178 / 255, 1),  # Hydro
    19: (241 / 255, 140 / 255, 31 / 255, 1),  # Gas thermal
    20: (0 / 255, 96 / 255, 1, 1),  # pumps
    21: (140 / 255, 140 / 255, 140 / 255, 1),  # Light gray other tech 1
    22: (145 / 255, 145 / 255, 145 / 255, 1),  # Light gray other tech 2
    23: (150 / 255, 150 / 255, 150 / 255, 1),  # Light gray other tech 3
    24: (155 / 255, 155 / 255, 155 / 255, 1),  # Light gray other tech 4
    25: (160 / 255, 160 / 255, 160 / 255, 1),  # Light gray other tech 5
    26: (150 / 255, 150 / 255, 150 / 255, 1),  # Light gray other tech 3
    27: (155 / 255, 155 / 255, 155 / 255, 1),  # Light gray other tech 4
    28: (160 / 255, 160 / 255, 160 / 255, 1),  # Light gray other tech 5
    29: (165 / 255, 165 / 255, 160 / 255, 1),  # Light gray other tech 5 #KP_MODIFIED
    30: (170 / 255, 170 / 255, 160 / 255, 1),  # Light gray other tech 5 #KP_MODIFIED
    31: (175 / 255, 175 / 255, 160 / 255, 1),  # Light gray other tech 5 #KP_MODIFIED
    32: (180 / 255, 180 / 255, 160 / 255, 1),  # Light gray other tech 5 #KP_MODIFIED
    33: (185 / 255, 185 / 255, 160 / 255, 1),  # Light gray other tech 5 #KP_MODIFIED
    34: (190 / 255, 190 / 255, 160 / 255, 1),  # Light gray other tech 5 #KP_MODIFIED
    35: (195 / 255, 195 / 255, 160 / 255, 1),  # Light gray other tech 5 #KP_MODIFIED
    36: (200 / 255, 200 / 255, 160 / 255, 1),  # Light gray other tech 5 #KP_MODIFIED

    50: (140 / 255, 140 / 255, 140 / 255, 1),  # ev_private
    51: (161 / 255, 135 / 255, 111 / 255, 1),  # ev_lcv
    52: (240 / 255, 79 / 255, 35 / 255, 1),  # ev_taxi
    53: (0 / 255, 96 / 255, 1, 1),  # ev_bicycle
    60: (1, 209 / 255, 26 / 255, 1),  # ev_bus
    61: (137 / 255, 174 / 255, 207 / 255, 1),  # ev_ferry
    70: (43 / 255, 161 / 255, 250 / 255, 1),  # ev_freight
}
