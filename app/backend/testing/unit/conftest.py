import numpy as np
import pytest

from models.users import User
from models.reported_fires import FireReports
from models.notification import Notification
from models.containment_lines import ContainmentLines
from models.role_request import RoleRequest


@pytest.fixture
def small_grids():
    def _make(H=5, W=5):
        """Generate minimal synthetic grid data for testing physical model inputs.

        Creates uniform weather blowing east and flat terrain dictionaries along with an unburned status matrix of dimensions (H, W).

        Parameters
        ----------
        H : int, default 5
            Height of spatial grid in cells.
        W : int, default 5
            Width of spatial grid in cells.

        Returns
        -------
        weather : dict of {str: np.ndaray}
            Dictionary containing uniform meteorological arrays (`wind_u`, `wind_v`, `rel_humidity`, `temperature`)
        static : dict of {str: np.ndarray}
            Dictionary containing uniform terrain and fuel feature arrays (`elevation`, `slope`, `aspect_sin`, `aspect_cos`, `fuel_load`, `dryness`)
        burn : np.ndarray
            (H, W) array of zeros representing an initially unburned state matrix.
        """
        weather = {
            "wind_u": np.full((H, W), 3.0, np.float32),
            "wind_v": np.zeros((H, W), np.float32),
            "rel_humidity": np.full((H, W), 30.0, np.float32),
            "temperature": np.full((H, W), 25.0, np.float32),
        }
        static = {
            "elevation": np.full((H, W), 500.0, np.float32),
            "slope": np.zeros((H, W), np.float32),
            "aspect_sin": np.zeros((H, W), np.float32),
            "aspect_cos": np.ones((H, W), np.float32),
            "fuel_load": np.full((H, W), 0.8, np.float32),
            "dryness": np.full((H, W), 0.6, np.float32),
        }
        burn = np.zeros((H, W), np.int8)
        return weather, static, burn

    return _make
