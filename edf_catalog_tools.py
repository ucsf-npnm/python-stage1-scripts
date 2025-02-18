""" edf_catalog_tools.py

Custom functions used in edf_catalog.py to create CSV file with EDF/HDF5 file metadata.

"""

# Import standard libraries
import pathlib
import os
import pandas as pd
import numpy as np
import mne
from datetime import datetime, timedelta


# Custom functions to build catalog
##Get paths to each edf file in patient's directory
def GetFilePaths(FileDirectory, FileFormat):
    FileNames = sorted(filter(lambda x: True if FileFormat in x else False, os.listdir(FileDirectory)))
    FilePaths = []
    for i in range(len(FileNames)):
        FilePaths.append(pathlib.Path(FileDirectory, FileNames[i]))
    print(f'{len(FilePaths)} files detected in folder')
    print('')
    return FilePaths

##Create dictionary object with each edf metadata
def ExtractFileMetadata(PatientID, FilePathList):
    edf_name     = []
    h5_name      = []
    edf_start    = []
    edf_end     = []
    edf_duration = []
    edf_sfreq    = []
    edf_nsample  = []
    edf_path     = []
    h5_path      = []
    timezone     = []

    for i in range(len(FilePathList)):
        raw          = mne.io.read_raw_edf(FilePathList[i])
        print('Tabulating info...')
        raw_start    = raw.info['meas_date']
        raw_duration = timedelta(seconds=len(raw)/raw.info['sfreq'])
        raw_n        = len(raw)
        raw_end      = raw_start + raw_duration

        ##Create name of future h5 file:
        date_string  = raw_start.strftime('%Y%m%d')
        time_string  = raw_start.strftime('%H%M%S')
        h5_string    = f'sub-{PatientID}_ses-stage1_task-continuous_acq-{date_string}_run-{time_string}_ieeg.h5'
        edf_name.append(str(FilePathList[i]).split("/")[-1])
        h5_name.append(h5_string)
        edf_start.append(raw_start.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S.%f'))
        edf_end.append(raw_end.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S.%f'))
        edf_duration.append(raw_duration.total_seconds())
        edf_nsample.append(raw_n)
        edf_sfreq.append(raw.info['sfreq'])
        edf_path.append(FilePathList[i])
        h5_path.append(pathlib.Path('/data_store0/presidio/nihon_kohden', PatientID, 'nkhdf5/edf_to_hdf5', h5_string))
        timezone.append('US/Pacific')
        print(f'File {i+1} completed')
        print('')

    DictObj = {
            'edf_name': edf_name,
            'edf_path': edf_path,
            'edf_start': edf_start,
            'edf_end': edf_end,
            'edf_duration': edf_duration,
            'edf_nsample': edf_nsample,
            'edf_sfreq': edf_sfreq,
            'h5_name': h5_name,
            'h5_path': h5_path,
            'time_zone': timezone
            }

    return DictObj

"""

End of code

"""
