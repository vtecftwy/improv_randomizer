import json
import logging
import os
import sys
from datetime import datetime
from functools import wraps
from IPython.display import display
from ipywidgets import (Text, Textarea, Button, Dropdown, HBox, VBox, IntSlider, Layout, AppLayout, GridspecLayout, Output, HTML, 
                        interactive, interactive_output, fixed)
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


class WidgetCast:
    def __init__(self, file=None) -> None:
        if file is None: 
            self.p2cast = ROOT/ 'cast.txt'
        else:
            self.p2cast = Path(file) if isinstance(file, str) else file
        assert self.p2cast.is_file()

        with open(self.p2cast, 'r') as fp:
            lines = fp.readlines()
            cast_names = [line.removesuffix('\n').strip() for line in lines]
        self.w = Text(value=', '.join(cast_names), description='Cast', layout=Layout(width='75%'))
        
    @property
    def value(self):
        return self.w.value

    def update(self, file=None):
        if file is None: 
            p2write = self.p2cast
        else:
            p2write = Path(file) if isinstance(file, str) else file

        with open(p2write, 'w') as fp:
            fp.write(self.w.value.replace(', ', '\n'))

    def __call__(self):
        display(self.w)

    def display(self):
        display(self.w)


class WidgetPrompts:
    def __init__(self, file=None) -> None:
        if file is None: 
            self.p2prompts = ROOT/ 'prompts.txt'
        else:
            self.p2prompts = Path(file) if isinstance(file, str) else file
        assert self.p2prompts.is_file()

        with open(self.p2prompts, 'r') as fp:
            lines = fp.readlines()
            self.prompts = [line.removesuffix('\n').strip() for line in lines]

        height = f"{16 * len(self.prompts)}px"
        self.w = Textarea(
            value='\n'.join(self.prompts), 
            description='Prompts', 
            layout=Layout(width='80%', height=height)
            )
                
    @property
    def value(self):
        return self.w.value

    def update(self, file=None):
        if file is None: 
            p2write = self.p2prompts
        else:
            p2write = Path(file) if isinstance(file, str) else file

        with open(p2write, 'w') as fp:
            fp.write(self.w.value)

    def __call__(self):
        display(self.w)

    def display(self):
        display(self.w)