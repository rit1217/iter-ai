import os
import logging


# Configure logging.
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO,
    force=True,
)

# Optimization config.
PLACE_CATEGORY_SERVICE_TIME = {
    'ACCOMMODATION': 0,
    'ATTRACTION': 120,
    'SHOP': 60,
    'RESTAURANT': 90
}
ACO_PARAMS = {
    'ANTS_NUM': 20,
    'MAX_ITER': 200,
    'BETA': 2,
    'Q0': 0.1
}
RHO = 0.3
DEPOT_INDEX = 0
