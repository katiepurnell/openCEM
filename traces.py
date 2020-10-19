""" Generate ev traces over the year / sample period"""
__author__ = "Katelyn Purnell"
__copyright__ = "n/a"
__credits__ = ["Katelyn Purnell"]
__license__ = "GPLv3"
__maintainer__ = "Katelyn Purnell"
__email__ = "n/a"

import locale
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize #
import json
from pathlib import Path

# input_file=open(Path("E:/OneDrive - UNSW/PhD/Modelling/openCEMKP/scenarios/bau/2021.json"), 'r')
# output_file=open('scenarios/bau/2021_ev_traces.json', 'w')
with open("E:/OneDrive - UNSW/PhD/Modelling/openCEMKP/scenarios/bau/2021.json") as f:
    # line_count = 1
    # while line_count <20:
    # for line in f:
        # j_content = json.loads(line)
        # line_count +=1
    data = json.load(f)
            # print(j_content)

FIELDS = ["vars.ev_dumb_charge.value"]#["sets.t.value"]#, "sets.regions", "vars.ev_dumb_charge"]
df = json_normalize(data["2021"])
df[FIELDS]
print(df)

# print(json.dumps(data, indent = 4, sort_keys=True))
# df = json_normalize(data, 'sets')
# print(df)

# json_df = pd.DataFrame(json.loads(data)['2021'])
# print(json_df)

# for item in json_decode:
#     my_dict={}
#     my_dict['title']=item.get('labels').get('en').get('value')
#     my_dict['description']=item.get('descriptions').get('en').get('value')
#     my_dict['id']=item.get('id')
#     print my_dict
# back_json=json.dumps(my_dict, output_file)
# output_file.write(back_json)
# output_file.close()
