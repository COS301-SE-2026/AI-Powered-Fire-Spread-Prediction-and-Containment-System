import numpy as np
import rasterio
from rasterio.enums import Resampling

#use 0.5 for values for now, will change when get 
FUEL_BASE_WEIGHTS = {
    10: 0.50# Tree cover
    # Shrubland
    # Grassland
    # Cropland
    # Built-up
    # Bare / sparse vegetation
    # Snow and ice
    # Permanent water bodies
    # Herbaceous wetland
    # Mangroves
    # Moss and lichen

}