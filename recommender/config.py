import os
import logging


# Configure logging.
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO,
    force=True,
)


# File configs.
TEMP_DIR = 'temp/'


# Data configs.
DATA_SUBDIRS = ['place_with_type', 'place_popularity', 'activity', 'attraction_type', 'place', 'opening_hour', 'cuisine_type', 'attraction_rank_vect', 'new_attraction_rank_vect']
DATA_FILENAMES = {x: f'{x}.csv.gz' for x in DATA_SUBDIRS}
DATA_FILEPATHS = {k: os.path.join(TEMP_DIR, v) for k, v in DATA_FILENAMES.items()}