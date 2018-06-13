# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 07:55:33 2017

@author: AtotheM
"""

import pandas as pd
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

##########################################################################################################
"""Import conductor resistance and reactance spreadsheet and create DataFrames of data"""
##########################################################################################################

conductorData = pd.read_excel(dir_path+"\Conductor Impedance.xlsx", skiprows=range(5)+[23,24],parse_cols=9)
conductorData = conductorData.drop(conductorData.columns[1], axis=1)

def dropKM(values):
    try:
        split = values.splitlines()
        km = float(split[0])
        feet = float(split[1])
    except Exception:
        return values
    return feet

conductorData = conductorData.applymap(dropKM)
conductorDataCopper = conductorData.drop(conductorData.columns[6:], axis=1)
conductorDataAlum = conductorData.drop(conductorData.columns[3:6], axis=1)

"""
AWG = AWG (up to 4/0) or kcmil (250 - 400) of wire
xL NF = Wire reactance in PVC and aluminum conduit per 1000 ft in ohms
xL F = Wire reactance in steel conduit per 1000 ft  in ohms
xR PVC = Wire resistance in PVC conduit per 1000 ft in ohms
xR Alum = Wire resistance in aluminum conduit per 1000 ft in ohms
xR Steel = Wire resistance in steel conduit per 1000 ft in ohms
"""
columnNames = ["AWG", "xL NF", "xL F", "xR PVC", "xR Alum", "xR Steel"]

conductorDataCopper.columns = columnNames
conductorDataAlum.columns = columnNames

conductorDataCopper = conductorDataCopper.set_index(["AWG"])
conductorDataCopper.index = conductorDataCopper.index.map(str)
conductorDataAlum = conductorDataAlum.set_index(["AWG"])
conductorDataAlum.index = conductorDataAlum.index.map(str)


##########################################################################################################
"""Other"""
##########################################################################################################

systemConfigDict = {
"12470/7200, 3PH": {"vLL":12470, "vLG":7200, "Phase":3},
"7200, 1PH": {"vLL":7200, "vLG":7200, "Phase":1},
"300/600, 1PH": {"vLL":600, "vLG":300, "Phase":1},
"600, 1PH": {"vLL":600, "vLG":600, "Phase":1},
"240/480, 1PH": {"vLL":480, "vLG":240, "Phase":1},
"480, 1PH": {"vLL":480, "vLG":480, "Phase":1},
"277, 1PH": {"vLL":277, "vLG":277, "Phase":1},
"208/120, 3PH": {"vLL":208, "vLG":120, "Phase":3},
"208, 1PH": {"vLL": 208, "vLG": 208, "Phase":1},
"120/240, 1PH": {"vLL":240, "vLG":120, "Phase":1},
"240, 1PH": {"vLL":240, "vLG":240, "Phase":1},
"120, 1PH": {"vLL":120, "vLG":120, "Phase":1},
"30/60, 1PH": {"vLL":60, "vLG":30, "Phase":1},
"60, 1PH": {"vLL":60, "vLG":60, "Phase":1},
"50, 1PH": {"vLL":50, "vLG":50, "Phase":1},
"15/30, 1PH": {"vLL":30, "vLG":15, "Phase":1},
"30, 1PH": {"vLL":30, "vLG":30, "Phase":1},
"12/24, 1PH":  {"vLL":24, "vLG":12, "Phase":1},
"24, 1PH": {"vLL":24, "vLG":24, "Phase":1}
}

voltageCompatDict = {
"12470": [12470, 7200],
"7200": [7200],
"600": [600, 300],
"480": [480, 277, 240],
"277": [277],
"240": [240, 120],
"208": [208, 120],
"120": [120, 60],
"60": [60, 30],
"50": [50],
"30": [30, 15],
"24": [24, 12]
}

compatWireSizes = ['14', '12', '10', '8', '6', '4', '3', '2', '1', '1/0', '2/0', '3/0', '4/0', '250', '300', '350', '400']
compatWireMaterial = ['copper', 'aluminum']
compatConduitMaterial = ['HDPE', 'PVC', "aluminum", "steel"]

WBASE = 1.0
VARBASE = 1.0

"""Example of how to access conductor data from DataFrame created above"""
# wireSize = 4
# print conductorDataCopper["xR PVC"].get(wireSize)
