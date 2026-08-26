import argparse

import numpy as np

from .load_real_dataset import RealDatasetConfig, load_real_dataset


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", default=RealDatasetConfig.hotspots_csv)
    ap.add_argument("--manifest", default=RealDatasetConfig.manifest_csv)
    ap.add_argument("--out", default="app/datasets/raw_data/ignition_dataset_real.npz")
    ap.add_argument(
        "--candidate-dilation",
        type=int,
        default=None,
    )

    args = ap.parse_args()

    cfg = RealDatasetConfig(
        hotspots_csv=args.csv,
        manifest_csv=args.manifest,
        candidate_dilation=args.candidate_dilation,
    )

    X, y, fire_ids = load_real_dataset(cfg)

    np.savez_compressed(args.out, X=X, y=y, fire_ids=fire_ids)

    print(f"wrote {args.out}")
    print(f"  X {X.shape} | fires {len(np.unique(fire_ids))} | pos_rate {y.mean():.5f}")


if __name__ == "__main__":
    main()
