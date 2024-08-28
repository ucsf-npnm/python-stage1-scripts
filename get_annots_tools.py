"""get_annots_tools.py

Custom functions to extract specific info from NK annotations. 

v1.0

"""

# Standard Libraries #
import pandas as pd
import numpy as np
import datetime
import pathlib
import os
import re

#Load all CSV files containing raw NK annotations based on patient's id (presidio only)
def LoadNKData(patient_id, path=None):
    main_path = pathlib.Path(f'/data_store0/presidio/nihon_kohden/', patient_id)
    if patient_id == 'PR01':
        nk_dir = 'NK_Annotations'
    if (patient_id == 'PR03') or (patient_id == 'PR05') or (patient_id == 'PR06'):
        nk_dir = 'NK_annotations'
    if patient_id == 'PR04':
        nk_dir = 'NK_annotations_2'
        
    if path == None:
        nk_path = pathlib.Path(main_path, nk_dir)
    if path != None:
        nk_path = pathlib.Path(path)
       
    FileNames = sorted(filter(lambda x: True if '.csv' in x else False, os.listdir(nk_path)))
    FilePaths = []
    for i in range(len(FileNames)):
        FilePaths.append(pathlib.Path(nk_path, FileNames[i]))

    #Create dataframe where each row represents a timestamped annotation saved by the NK. 
    df_IN = []
    for path in FilePaths:
        df_OUT = pd.read_csv(path,
                             delimiter='\t',
                             header=None,
                             names=['EventType', 'EventTimestamp', 'FileID'])
        df_IN.append(df_OUT)
    df_OUT = pd.concat(df_IN).reset_index(drop=True)
    df_OUT.EventTimestamp = pd.to_datetime(df_OUT.EventTimestamp, format='%Y/%m/%d %H:%M:%S %f')

    NewDataFrame = df_OUT.sort_values(by='EventTimestamp').reset_index(drop=True)
    
    return NewDataFrame

#Get all disconnects/reconnects of mini junction box 
def GetDataDisconnects(DataFrame):
    Disconnects = DataFrame.loc[DataFrame['EventType'].str.contains('Mini junction box disconnected')].drop_duplicates(subset='EventTimestamp').reset_index(drop=True)
    Disconnects['EventType']= 'disconnect'
    Reconnects = DataFrame.loc[DataFrame['EventType'].str.contains('Mini junction box connected')].drop_duplicates(subset='EventTimestamp').reset_index(drop=True)
    Reconnects['EventType']= 'reconnect'
    MergedDataFrame = pd.concat([Disconnects, Reconnects], ignore_index=True).sort_values(by='EventTimestamp').reset_index(drop=True).drop(columns='FileID')

    del Disconnects, Reconnects

    flags = []
    for i in list(range(len(MergedDataFrame.EventType)-1)):
        if MergedDataFrame.EventType[i] != MergedDataFrame.EventType[i+1]:
            flags.append('paired')
        if MergedDataFrame.EventType[i] == MergedDataFrame.EventType[i+1]:
            flags.append('unpaired')

    if MergedDataFrame.EventType.iloc[-2] != MergedDataFrame.EventType.iloc[-1]:
        flags.append('paired')
    if MergedDataFrame.EventType.iloc[-2] == MergedDataFrame.EventType.iloc[-1]:
        flags.append('unpaired')

    MergedDataFrame['Flag'] = flags

    DisconnectsPaired = MergedDataFrame.loc[(MergedDataFrame.EventType=='disconnect') & (MergedDataFrame.Flag=='paired')].reset_index(drop=True).rename(columns={'EventTimestamp':'DisconnectStart'})
    ReconnectsPaired = MergedDataFrame.loc[(MergedDataFrame.EventType=='reconnect') & (MergedDataFrame.Flag=='paired')].reset_index(drop=True).rename(columns={'EventTimestamp':'DisconnectStop'})

    NewDataFrame = pd.concat([DisconnectsPaired, ReconnectsPaired], axis=1).drop(columns=['EventType', 'Flag'])
    NewDataFrame['DisconnectDuration'] = [x.total_seconds() for x in NewDataFrame.DisconnectStop-NewDataFrame.DisconnectStart]

    del MergedDataFrame, DisconnectsPaired, ReconnectsPaired

    return NewDataFrame

#Get all stimulation triggers delivered in tabulated CSV
def GetStimulation(DataFrame):
    StimStart = DataFrame.loc[DataFrame['EventType'].str.contains('Stim Start')]
    StimStartClean = StimStart.copy().drop(columns=['EventType', 'FileID'])
    StimStartClean['TriggerKey'] = [x.split(' ')[1] for x in StimStart.EventType]
    StimStartClean['Settings'] = [x.replace('Stim Start ', '') for x in StimStart.EventType]
    StimStop = DataFrame.loc[DataFrame['EventType'].str.contains('Stim Stop')]
    StimStopClean = StimStop.copy().drop(columns=['EventType', 'FileID'])
    StimStopClean['TriggerKey'] = [x.split(' ')[1] for x in StimStop.EventType]
    StimStopClean['Settings'] = [x.replace('Stim Stop ', '') for x in StimStop.EventType]
    MergedDataFrame = pd.concat([StimStartClean, StimStopClean], ignore_index=True).sort_values(by='EventTimestamp').drop_duplicates(subset='EventTimestamp').reset_index(drop=True)

    del StimStart, StimStartClean, StimStop, StimStopClean
    
    stim_condition = []
    stim_condition_raw = [x.split(' ')[-1] for x in MergedDataFrame.Settings]
    for _ in stim_condition_raw:
        if '[SH]' in _:
            stim_condition.append('Sham')
        if '[SH]' not in _:
            stim_condition.append('Active')

    MergedDataFrame['StimCondition'] = stim_condition
    MergedDataFrame['PosContact'] = [x.split('-')[0].replace(' ', '') for x in MergedDataFrame.Settings]
    MergedDataFrame['NegContact'] = [(re.split('(\d+)',x.split('-')[1])[0]+re.split('(\d+)',x.split('-')[1])[1]).replace(' ', '') for x in MergedDataFrame.Settings]
    MergedDataFrame['Amplitude'] = [float(x.split(' ')[-2]) for x in MergedDataFrame.Settings]

    flags = []
    for i in list(range(len(MergedDataFrame.TriggerKey)-1)):
        if MergedDataFrame.TriggerKey[i] != MergedDataFrame.TriggerKey[i+1]:
            flags.append('paired')
        if MergedDataFrame.TriggerKey[i] == MergedDataFrame.TriggerKey[i+1]:
            flags.append('unpaired')

    if MergedDataFrame.TriggerKey.iloc[-2] != MergedDataFrame.TriggerKey.iloc[-1]:
        flags.append('paired')
    if MergedDataFrame.TriggerKey.iloc[-2] == MergedDataFrame.TriggerKey.iloc[-1]:
        flags.append('unpaired')

    MergedDataFrame['Flag'] = flags

    #Create clean output
    StartStimPaired = MergedDataFrame.loc[(MergedDataFrame.TriggerKey=='Start') & (MergedDataFrame.Flag=='paired')].reset_index(drop=True).rename(columns={'EventTimestamp':'StimStart'}).drop(columns=['TriggerKey', 'Flag', 'Settings'])
    StopStimPaired = MergedDataFrame.loc[(MergedDataFrame.TriggerKey=='Stop') & (MergedDataFrame.Flag=='paired')].reset_index(drop=True).rename(columns={'EventTimestamp':'StimStop'}).drop(columns=['TriggerKey', 'Flag', 'Settings'])

    StartStimUnpaired = MergedDataFrame.loc[MergedDataFrame.Flag=='unpaired'].reset_index(drop=True).rename(columns={'EventTimestamp':'StimStart'}).drop(columns=['TriggerKey','Flag', 'Settings'])

    MergedStimPaired = pd.concat([StartStimPaired, StopStimPaired], axis=1).T.drop_duplicates().T
    MergedStimPaired['TrainDuration'] = [x.total_seconds() for x in MergedStimPaired.StimStop-MergedStimPaired.StimStart]

    NewDataFrame = pd.concat([MergedStimPaired, StartStimUnpaired], ignore_index=True).sort_values(by='StimStart').reset_index(drop=True)
    col1 = NewDataFrame.pop('StimStop')
    NewDataFrame.insert(1, 'StimStop', col1)

    del MergedDataFrame, StartStimPaired, StopStimPaired, StartStimUnpaired, MergedStimPaired

    return NewDataFrame

"""End of code"""