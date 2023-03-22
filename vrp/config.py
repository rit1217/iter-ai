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
    'ANTS_NUM': 10,
    'MAX_ITER': 200,
    'BETA': 2,
    'Q0': 0.1
}
DEPOT_INDEX = 0


# Data config.
# DATA_SUBDIRS = ['item_master']
# DATA_FILENAMES = {x: f'{x}.csv.gz' for x in DATA_SUBDIRS}
# DATA_FILEPATHS = {k: os.path.join(TEMP_DIR, v) for k, v in DATA_FILENAMES.items()}