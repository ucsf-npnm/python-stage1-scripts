"""get_annots.py

Main code to extract specific info from NK annotations.

v1.0

"""

# Standard Libraries #
import pandas as pd
import numpy as np
import datetime
import pathlib
import os
import re

# Custom functions #
from get_annots_tools import LoadNKData, GetDataDisconnects, GetStimulation

# User-specified inputs #
patient_id = 'PR06'
stim_on = False
disconnects_on = True

INPUT_PATH = None
OUTPUT_PATH = '/userdata/dastudillo/patient_data/stage1/'

# Main code #
concatenated_annots = LoadNKData(patient_id, INPUT_PATH)

if stim_on == True:
    stim_annots = GetStimulation(concatenated_annots)
    fn_stim = f'{patient_id}_Stage1_StimulationParameters.csv'
    stim_annots.to_csv(pathlib.Path(OUTPUT_PATH,fn_stim), index=False)

if disconnects_on == True:
    disconnects_annots = GetDataDisconnects(concatenated_annots)
    fn_disc = f'{patient_id}_Stage1_DataDisconnects.csv'
    disconnects_annots.to_csv(pathlib.Path(OUTPUT_PATH,fn_disc), index=False)


"""End of code"""
