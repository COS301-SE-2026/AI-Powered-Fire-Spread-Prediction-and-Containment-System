#to execute:
#python app/datasets/scripts/calculate_ruleset_weights.py
#only need to exe once

import json
from pathlib import Path
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
DATASETS_DIR = SCRIPT_DIR.parent

PARAMS_CSV = DATASETS_DIR / "raw_data" / "fbfm40_parameters.csv"
LOOKUP_CSV = DATASETS_DIR / "raw_data" / "LF2025_FBFM40.csv"
XWALK_TXT = DATASETS_DIR / "raw_data" / "XWALK_EVT_EVG_EVS.txt"
RULESET_TXT = DATASETS_DIR / "raw_data" / "Master_Rulesets.txt"

OUTPUT_JSON = DATASETS_DIR / "processed" / "worldcover_base_weights.json"
OUTPUT_CSV = DATASETS_DIR / "processed" / "worldcover_base_weights.csv"

CHUNK_SIZE = 100000

WORLDCOVER_LABELS = {
    10: "Tree cover",
    20: "Shrubland", 
    30: "Grassland",
    40: "Cropland",
    50: "Built-up",
    60: "Bare / sparse vegetation",
    70: "snow and ice",
    80: "Permanent water bodies",
    90: "Herbaceous wetland",
    95: "Mangroves",
    100: "Moss and lichen",
}

def build_evt_to_worldcover_map(xwalk_path: Path) -> dict[int, int]:
    """maps evt numeic code to an official esa worldcover class id"""

    xwalk_file= Path(xwalk_path)
    if not xwalk_file.exists():
        raise FileNotFoundError(f"Xwalk text file not found at: {xwalk_path}")

    df_xwalk = pd.read_csv(xwalk_file, sep=";", header=None, engine="python", on_bad_lines="skip")

    evt_wc_map = {}

    for _, row in df_xwalk.iterrows():
        try:
            evt_code = int(row.iloc[0])
        except (ValueError, TypeError):
            continue

        text_info = (
            " ".join([
                str(val) for val in row.values]).lower().strip()
        )

        if "water" in text_info:
            wc_class = 80
        elif any(w in text_info for w in ["developed", "urban"]): 
            wc_class = 50
        elif any(w in text_info for w in ["snow", "ice", "glacier"]):
            wc_class = 70 
        elif any(w in text_info for w in ["marsh", "bog"]):
            wc_class = 90
        elif any(w in text_info for w in ["mangrove"]):
            wc_class = 95
        elif any(w in text_info for w in ["crop", "agriculture", "field"]):
            wc_class = 40
        elif any(w in text_info for w in ["tree", "forest", "woodland", "hardwood", "conifer"]):
            wc_class = 10
        elif any(w in text_info for w in ["shrub", "chaparral", "sagebrush"]):
            wc_class = 20
        elif any(w in text_info for w in ["grass", "herbaceous", "steppe", "prairie"]):
            wc_class = 30
        elif any(w in text_info for w in ["sparse", "rock", "barren"]):
            wc_class = 60
        else:
            wc_class = 30

        evt_wc_map[evt_code] = wc_class

        return evt_wc_map

def build_fbfm_weight_map(params_path: Path, lookup_path: Path) -> dict[int, float]:
    """Reads fbfm40 csv and normalises weights"""

    df_params = pd.read_csv(params_path)
    df_lookup = pd.read_csv(lookup_path)

    df_params["total_tons_per_acre"] = (
        df_params["load_1hr"] +
        df_params["load_10hr"] +
        df_params["load_100hr"] +
        df_params["load_live_herb"] +
        df_params["load_live_woody"]
    )

    max_load = df_params["total_tons_per_acre"].max()
    df_params["normalised_weight"] = (
        df_params["total_tons_per_acre"] / (max_load if max_load > 0 else 1.0)
    ).round(4)

    name_to_weight = dict(zip(df_params["model_name"], df_params["normalised_weight"]))

    fbfm_weight_map = {}

    for _, row in df_lookup.iterrows():
        try:
            code = int(row["VALUE"])
            model_name = str(row["FBFM40"]).strip()
            if model_name in name_to_weight:
                fbfm_weight_map[code] = name_to_weight[model_name]
        except (ValueError, TypeError):
            continue

    return fbfm_weight_map

def calculate_ruleset_weights():
    """integrate xwalk and fbfm params, stream chunk blocks and aggregate avg base fuel weights/ worldcover class"""

    print("Load EVT and WorldCover xwalk mapping")
    evt_wc_map = build_evt_to_worldcover_map(XWALK_TXT)
    print(f"Mapped {len(evt_wc_map):,} unique EVT codes")

    print("Load FBFM40 physical fuel loading params")
    fbfm_weight_map = build_evt_to_worldcover_map(PARAMS_CSV)

    wordlcover_aggregates = {
        wc_id: {"weight_sum": 0.0, "count": 0} for wc_id in WORLDCOVER_LABELS
    }

    rules_file = Path(RULESET_TXT)
    if not rules_file.exists():
        raise FileNotFoundError(f"Master ruelset not found at: {RULESET_TXT}")

    print(f"Streaming {rules_file.name} in chunk of {CHUNK_SIZE:,} rows")

    chunk_counter = pd.read_csv(
        rules_file,
        sep=";",
        chunksize=CHUNK_SIZE,
        low_memory=False,
        on_bad_lines="skip",
    )

    for  i, chunk in enumerate(chunk_counter):
        evt_col_index = 0
        fbfm_col_index = 8 if len(chunk.columns) > 8 else 1

        #nan is filled woth 30 as standard if there's no data
        chunk["wc_class"] = (
            chunk.iloc[:, evt_col_index].astype(int).map(evt_wc_map).fillna(30).astype(int)
        )

        chunk["weight"] = (
            chunk.iloc[:, fbfm_col_index].astype(int).map(fbfm_weight_map).fillna(0.0)
        )

        #aggregate sums woth counts
        grouped = (
            chunk.groupby("wc_class")["weight"].agg(["sum", "count"]).reset_index()
        )

        for _, row in grouped.iterrows():
            wc_id = int(row["wc_class"])
            if wc_id in wordlcover_aggregates:
                wordlcover_aggregates[wc_id]["weight_sum"] += float(row["sum"])
                wordlcover_aggregates[wc_id]["count"] += int(row["count"])

        print(f"Chunk {i+1} finished processing")

        print("Final base weight avg and export output")
        final_results = []
        json_lookup = {}

        for wc_id, data in sorted(wordlcover_aggregates.items()):
            avg_weight = (
                round(data["weight_sum"] / data["count"], 4) if data["count"] > 0 else 0.0
            )
            final_results.append({
                "WorldCover_Class": wc_id,
                "Description": WORLDCOVER_LABELS[wc_id],
                "Base_Fuel_Weight": avg_weight,
                "Total_Rules_Evaluated": data["count"],
            })
            json_lookup[wc_id] = avg_weight

        #save for runtime loading
        Path(OUTPUT_JSON).parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_JSON, "w") as f:
            json.dump(json_lookup, f, indent=4)

        #save csv summary
        pd.DataFrame(final_results).to_csv(OUTPUT_CSV, index=False)

        print("\nCalculations finished successfully")
        print(f"json lookup dictionary exported to: {OUTPUT_JSON}")
        print(f"csv summary report exported to: {OUTPUT_CSV}")

if __name__ == "__main__":
    calculate_ruleset_weights()