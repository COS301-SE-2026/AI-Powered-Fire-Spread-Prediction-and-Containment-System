"""
Truncates the weather timeline in each .npz fire event file to a sane simulation window (default
72 hours = 288 DCA steps), and corrects the stored duration_hours to match. Backs up originals 
before overwriting

Usage:
    python3 fix_npz_duration.py --data-dir app/datasets/processed/dca_historical_events
"""

import argparse
import shutil
from pathlib import Path

import numpy as np

MAX_HOURS = 72

def fix_file(path: Path, max_hours: int) -> None:
    data = dict(np.load(path, allow_pickle=True))
    
    n_hours = data["weather_u"].shape[0]
    if n_hours <= max_hours:
        print(f"{path.name}: already OK ({n_hours}h) skipping")
        return
    
    for key in ("weather_u", "weather_v", "weather_temp", "weather_rh"):
        data[key] = data[key][:max_hours]
        
    data["duration_hours"] = np.array(max_hours)
    
    backup_path = path.with_suffix(".npz.bak")
    if not backup_path.exists():
        shutil.copy2(path, backup_path)
        
    np.savez_compressed(path, **data)
    print(f"{path.name}: truncated {n_hours}h -> {max_hours}h (backup saved to {backup_path.name})")
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--max-hours", type=int, default=MAX_HOURS)
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    npz_files = sorted(data_dir.glob("*.npz"))
    print(f"Found {len(npz_files)} .npz files in {data_dir}")
    
    for p in npz_files:
        fix_file(p, args.max_hours)
        
    print("\nDone")
    
if __name__ == "__main__":
    main()