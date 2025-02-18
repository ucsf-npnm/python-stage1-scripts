""" edf_catalog.py

Extracts and tabulates metadata from EDF files collected over stage 1. For each EDF file, assigns HDF5 name and path.
Outputs CSV file in assigned outdir variable

"""

# Standard Libraries #
import pathlib
import pandas as pd

# Custom functions #
from edf_catalog_tools import GetFilePaths, ExtractFileMetadata

# User-specified inputs #
patient_id     = 'PR06' #presidio subject ID
stage1_maindir = '/data_store0/presidio/nihon_kohden' #main directory storing presidio data from stage 1
edf_dir        = pathlib.Path(stage1_maindir, patient_id, patient_id) #directory storing raw EDF files
outdir         = pathlib.Path(stage1_maindir, patient_id, 'nkhdf5') #directory storing HDF5 files converted from EDF files

# Main code #
edf_file_paths = GetFilePaths(edf_dir, 'edf')
edf_dict       = ExtractFileMetadata(patient_id, edf_file_paths)
edf_catalog    = pd.DataFrame(edf_dict)

edf_catalog.to_csv(pathlib.Path(outdir, f'{patient_id}_edf_catalog.csv'), index=False)
print(f'{patient_id}_edf_catalog.csv has been created and saved in {outdir}')

"""

End of code

"""
