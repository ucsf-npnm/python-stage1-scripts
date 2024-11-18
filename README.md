# Stage 1 scripts:
Scripts to tabulate, analyze, visualize Stage 1 data (neural/behavioral)

## Extract info from NK annotations
Extract auto-generated annotations in CSV files exported from NK-CDS
version v1.0
author: Daniela Astudillo

### `get_annots.py`:
Main code, contains user-specified inputs that can be modified according to what type of annotations you want to extract:
* `patient_id`: _string_, ID assigned to subject in the study (for Presidio, use format PRX).
* `stim_on`: _boolean_, if True, code will extract and tabulate all stimulation timestamps and parameters delivered during Stage 1, ordered by timestamp.
* `disconnects_on`: _boolean_, if True, code will extract and tabulate all disconnects and reconnects in the mini junction box, ordered by timestamp.
* `INPUT_PATH`: _string_ or _None_, path to CSV files with raw NK annotations. If you are extracting annotations from PR01, PR03, PR04, PR05, or PR06, set to _None_ as the path will be imported from `get_annots_tools.py`.
* `OUTPUT_PATH`: _string_, path to folder where code will save output CSV file(s).   

### `get_annots_tools.py`:
Custom functions imported in `get_annots.py`. 
