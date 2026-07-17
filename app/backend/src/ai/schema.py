# Features list, burn-state codes, constants
# Contract between pipeline stages and between machines

WEATHER_FEATURES = [
    "wind_u",   # east-west component
    "wind_v",   # north-south component
    "rel_humidity", # percentage
    "temperature", # deg celsius
]

# Fuel raster layers
STATIC_FEATURES = [
    "elevation",    # m
    "slope",    # degrees
    "aspect_sin",   
    "aspect_cos",   
    "fuel_load",    
    "dryness",
]

# Neighbour burn-state features - computed from DCA burn map each tick
NEIGHBOUR_FEATURES = [
    "n_burning_neighbours",
    "upwind_burning",   # 0/1: cell the wind blows FROM is burning
    "downslope_burning",    # 0/1: a lower-elevation neighbour burning
    "dist_to_fire",     # cells to nearest burning cell capped
]

FEATURES = WEATHER_FEATURES + STATIC_FEATURES + NEIGHBOUR_FEATURES
LABEL = "ignited_next_tick"

UNBURNED, BURNING, BURNED = 0, 1, 2     # Burn-state codes on grid (also shared with DCA)

DIST_CAP = 10.0     # Cap for dist to fire ("very far" is a value and not a gradient)

SCHEMA_VERSION = 1      # Bump when features/semantics change. Stored in every artifact