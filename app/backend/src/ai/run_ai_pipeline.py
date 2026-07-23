import numpy as np
import torch

from .dca import run_dca

def test_grid(H: int = 30, W: int =30) -> tuple[dict, dict]:
    weather_grids = {
        "wind_u": np.full((H,W), 3.0, dtype=np.float32),
        "wind_v": np.full((H,W), 1.0, dtype=np.float32),
        "rel_humidity": np.full((H,W), 35.0, dtype=np.float32),
        "temperature": np.full((H,W), 28.0, dtype=np.float32),
    }

    static_grids ={
        "elevation": np.zeros((H,W), dtype=np.float32),
        "slope": np.zeros((H,W), dtype=np.float32),
        "aspect_sin": np.zeros((H,W), dtype=np.float32),
        "aspect_cos": np.zeros((H,W), dtype=np.float32),
        "fuel_load": np.full((H,W), 0.5, dtype=np.float32),
        "dryness": np.full((H,W), 0.5, dtype=np.float32),
    }

    return weather_grids, static_grids

def main():
    weather_grids, static_grids = test_grid()

    params = {
        "a": torch.tensor(0.1),
        "p_h": torch.tensor(0.4),
        "c_1": torch.tensor(0.1),
        "c_2": torch.tensor(0.1),
        "p_continue": torch.tensor(0.6),
    }

    print(f"DCA is running | device currently being used: device={'cuda' if torch.cuda.is_available else 'cpu'}")
    history = run_dca(weather_grids, static_grids, n_steps=15, params=params)

    print(f"\n{'tick':>4} | {'burning':>8} | {'burned':>7}")
    print("-"*6)

    for t, grid in enumerate(history):
        burning_count = int((grid == 1).sum())
        burned_count = int((grid == 2).sum())
        print(f"{t:>4} | {burning_count:>8} | {burned_count:>7}")

if __name__ == "__main__":
    main()