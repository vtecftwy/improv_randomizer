import logging
import os
import sys
from datetime import datetime
from functools import wraps
from pathlib import Path

# Setup path to package and modules
# TODO: correct this line after transforming this is a package
ROOT = Path(__file__).parent
os.makedirs(ROOT / 'logs', exist_ok=True)

def logthis(*args):
    text = ' '.join([str(element) for element in args])
    logging.info(text)

def monitor_fn(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        logthis(f"Entering `{fn.__name__}`")
        res = fn(*args, **kwargs)
        logthis(f"Exiting  `{fn.__name__}`")
        return res
    return wrapper
    # return fn

def setup_logging(filename=None):
    
    # Setup logging file
    if filename is None:
        p2log = ROOT / 'logs/_short.log'
    else:
        p2log = ROOT / f'logs/{filename}'
    if not p2log.is_file():
        p2log.touch()

    # Configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(message)s',
        datefmt='%H:%M:%S'
        )
    # Create a file handler to log to a file
    file_handler = logging.FileHandler(
        filename=p2log,
        mode='a',   
        encoding='utf-8'
        )
    file_handler.setLevel(logging.DEBUG)  # Set the log level for the file handler
    file_handler.setFormatter(
        fmt=logging.Formatter(
            fmt='%(asctime)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
            )    
        )
    # Add the file handler to the root logger
    logging.getLogger('').addHandler(file_handler)

    logthis(f"{'='*50}")
    logthis(f" {'New Session: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^48s}")
    logthis(f"{'='*50}")