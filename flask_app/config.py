import os
import logging
import json
from PIL import Image

# Folder paths
BASE_DIR = os.getcwd()
RAW_FOLDER = os.path.join(BASE_DIR, 'images_raw')
UNRATED_FOLDER = os.path.join(BASE_DIR, 'images_unrated')
RATED_FOLDER = os.path.join(BASE_DIR, 'images_rated')
DEBUG_FOLDER = os.path.join(BASE_DIR, 'images_debug')
PREPROCESS_FOLDER = os.path.join(BASE_DIR, 'images_preprocessed')
METADATA_FILE= os.path.join(PREPROCESS_FOLDER, "metadata.jsonl")
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'images_log.json')
OPERATION_LOG_FILE = os.path.join(BASE_DIR, 'logs', 'operations.log')
LOG_ARCHIVE_FOLDER = os.path.join(BASE_DIR, 'logs_archive')
THUMBNAIL = "_thumb"

# Constants
# ---------------- Image processing ----------------
IMAGE_BATCH_SIZE = 10  # Number of images to serve per batch
PARTITION_SIZE = 100  # Number of images per partition
SERVE_TIMEOUT_SECONDS = 300  # seconds (5 minutes)
# ---------------- Scheduler ----------------
SCHEDULER_INTERVAL_MOVE_TO_UNRATED = 1 * 60 * 60  # (hour)
SCHEDULER_INTERVAL_CHECK_LOG_SIZE = 0.5 * 60 * 60 # (hour)
SCHEDULER_INTERVAL_CREATE_THUMBNAILS = 1 * 60 * 60 # (hour)
SCHEDULER_INTERVAL_PREPROCESSING_IMAGE = 24 * 60 * 60 # (hour)
MAX_LOG_FILE_SIZE_BYTES = 20 * 1024 * 1024  # MB
# ---------------- Image compression ----------------
MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024  # MB
Image.MAX_IMAGE_PIXELS = 933120000
IMAGE_THUMBNAIL_SIZE = 1024
IMAGE_PREPROCESS_SIZE = 1024
# ---------------- Score ----------------
SCORE_MAP = {
    "-1": 0.0, "0": 0.0, "1": 0.2, "2": 0.4, "3": 0.6, "4": 0.8, "5": 1.0
}

# Configure logging
logging.basicConfig(
    filename=OPERATION_LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def log_operation(message):
    """Log an operation message."""
    logging.info(message)


if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as log_file:
        json.dump({}, log_file)

for folder in [RAW_FOLDER, UNRATED_FOLDER, RATED_FOLDER, DEBUG_FOLDER, LOG_ARCHIVE_FOLDER, PREPROCESS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
