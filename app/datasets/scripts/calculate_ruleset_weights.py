import json
from pathlib import Path
import numpy as np
import pandas as pd

PARAMS_CSV = "../raw_data/LF2025_FBFM40.csv"
XWALK_TXT = "../raw_data/XWALK_EVT_EVG_EVS.txt"
RULESET_TXT = "../raw_data/Master_Rilesets.txt"

OUTPUT_JSON = "../processed/worldcover_base_weights.json"
OUTPUT_CSV = "../processed/worldcover_base_weights.csv"

CHUNK_SIZE = 100000

WORLDCOVER_LABELS = {
    
}