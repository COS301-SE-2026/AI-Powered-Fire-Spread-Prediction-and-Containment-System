import pandas as pd
import numpy as np
import json
from pathlib import Path

PARAMS_CSV = "raw_data/fbfm40_parameters.csv"
RULESET_TXT = "raw_data/Master_Rulesets.txt"
OUTPUT_JSON = "processed/worldcover_base_weights.json"
OUTPUT_CSV = "processed/worldcover_base_weights.csv"

CHUNK_SIZE = 100000

WORLDCOVER_LABELS = {
    10: "Tree cover",
    20: "Shrubland",
    30: "Grassland",
    40: "Cropland",
    50: "Built-up",
    60: "Bare / sparse vegetation",
    70: "Snow and ice",
    80: "Permanent water bodies",
    90: "Herbaceous wetland",
    95: "Mangroves",
    100: "Moss and lichen"
}

def fbfm_code_to_worldcover_class(fbfm_code: int) -> int:
    """Map FBFM40 int codes to worldcover class ints (10-100)"""
    if fbfm_code in [91]:
        return 50 #"Built-up"/urban
    if fbfm_code in [92, 99]:
        return 60 #"Bare / sparse vegetation",
    if fbfm_code in [93]:
        return 80 #"Permanent water bodies",
    if fbfm_code in [98]:
        return 70 #"Snow and ice",
    if 101 <= fbfm_code <= 124:
        return 30 #"Grassland",
    if 141 <= fbfm_code <= 149 :
        return 20 #"Shrubland",
    if 161 <= fbfm_code <= 204:
        return 10 #tree cover/ timber /slash
    return 60 #fallback, "Bare / sparse vegetation"

def build_weight_map_from_params(params_path: str) -> dict[int, float]:
    #website down today (22/07/2026) so will download csv file tomorrow
    """compute dynamic norm weights from rmrs-gtr-153 physical fuel loads"""
    df = pd.read_csv(params_path)

    df["total_tons_per_acre"] = (
        df["load_1hr"] + df["load_10hr"] + df["load_100hr"] +
        df["load_live_herb"] + df["load_live_woody"]
    )

    max_load = df["total_tons_per_acre"].max()
    df["normalised_weight"] = (df["total_tons_per_acre"] / (max_load if max_load > 0 else 1.0)).round(4)

    return dict(zip(df["fbfm_code"].astype(int), df["normalised_weight"]))

def calc_ruleset_weights():
    """Stream Master_Rulesets.txt and aggregate base weights per Worldcover class"""
    weight_map = build_weight_map_from_params(PARAMS_CSV)

    worldcover_aggregates = {
        wc_id: {"weight_sum": 0.0, "count": 0}
        for wc_id in WORLDCOVER_LABELS.keys()
    }

    rules_file = Path(RULESET_TXT)
    if not rules_file.exists():
        raise FileNotFoundError(f"Missinf ruleset file at {RULESET_TXT}")
    
    print(f"Streaming {rules_file.name} in chunks of {CHUNK_SIZE:,} rows")

    chunk_count = pd.read_csv(
        rules_file,
        sep=";",
        chunksize=CHUNK_SIZE,
        low_memory=False,
        on_bad_lines="skip"
    )

    for i, chunk in enumerate(chunk_count):
        # id fbfm columns
        fbfm_col = next((c for c in ["FBFM40", "FBFM40_Code", "Fuel_Model"] if c in chunk.columns), None)
        if not fbfm_col:
            raise KeyError("FBFM code column not found in text file")
        
        chunk["fbfm_code"] = chunk[fbfm_col].astype(int)
        chunk["weight"] = chunk["fbfm_code"].map(weight_map).fillna(0.0)
        chunk["wc_class"] = chunk["fbfb_code"].apply(fbfm_code_to_worldcover_class)

        grouped = chunk.groupby("wc_class")["weight"].agg(["sum", "count"]).reset_index()

        for _, row in grouped.iterrows():
            wc_id = int(row["wc_class"])
            if wc_id in worldcover_aggregates:
                worldcover_aggregates[wc_id]["weight_sum"] += float(row["sum"])
                worldcover_aggregates[wc_id]["count"] += int(row["count"])

            print(f"Chunk {i+1} processed")


        final_results = []
        json_lookup = {}

        for wc_id, data in sorted(worldcover_aggregates.items()):
            avg_weight = round(data["weight_sum"] / data["count"], 4) if data["count"] > 0 else 0.0
            final_results.append({
                "WorldCover_Class": wc_id,
                "Description": WORLDCOVER_LABELS[wc_id],
                "Base_Fuel_Weight": avg_weight,
                "Rules_Evaluated": data["count"]
            })
            json_lookup[wc_id] = avg_weight

        Path(OUTPUT_JSON).parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_JSON, "w") as f:
            json.dump(json_lookup, f, indent=4)

        pd.DataFrame(final_results).to_csv(OUTPUT_CSV, index=False)
        print(f"\nSaved JSON lookup to: {OUTPUT_JSON}")
        print(f"Saved CSV lookup to: {OUTPUT_CSV}")

    if __name__ == "__main__":
        calc_ruleset_weights()
