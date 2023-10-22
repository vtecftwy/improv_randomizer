import json
import logging
import os
import sys
from configparser import ConfigParser
from datetime import datetime
from functools import wraps
from IPython.display import display, display_html
from ipywidgets import Text, Label, Textarea, Button, Layout, GridspecLayout, SelectMultiple
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

def get_config():
    """Identifies the config file, loads it and returns a config dictionary."""
    # Select configuration file: config.cfg, config-default.cfg, first of any other *.cfg    
    if (ROOT/'config.cfg').is_file():
        p2config = ROOT / 'config.cfg'
        logthis(f"Using config.cfg file: {p2config}")
    elif (ROOT/'config-default.cfg').is_file():
        p2config = ROOT / 'config-default.cfg'
        logthis(f"Using config-default.cfg file: {p2config}")
    elif len(list(ROOT.glob('config*.cfg'))) > 0:
        p2config = list(ROOT.glob('config*.cfg'))[0]
        logthis(f"Using first custom config file: {p2config}")
    else:
        raise FileNotFoundError('No configuration file found. Should be a *.cfg file')

    cfg = ConfigParser()
    cfg.read(p2config)
    config_dict = {k:v for k,v in cfg['DEFAULT'].items()}
    numerical_values = ['duration-minutes']
    for k in numerical_values:
        config_dict[k] = int(config_dict[k])
    return config_dict

def get_paths():
    config_dict = get_config()
    p2games = ROOT/ f"config/{config_dict['cfg-folder']}/{config_dict['games']}"
    p2cast = ROOT/ f"config/{config_dict['cfg-folder']}/{config_dict['cast']}"
    p2prompts = ROOT/ f"config/{config_dict['cfg-folder']}/{config_dict['prompts']}"
    return p2games, p2cast, p2prompts

# Function for ipython widgets
def create_label(value, width='80%'):
    return Label(value=value, layout=Layout(width=width))

def create_text(description, value, width='80%'):
    return Text(value=value, description=description, layout=Layout(width=width))

def create_button(description, button_style='info', icon='check', on_click=None):
    btn = Button(
        description=description,
        button_style=button_style, # 'success', 'info', 'warning', 'danger' or ''
        icon=icon
    )
    if on_click is not None:
        btn.on_click(on_click)
    return btn

def create_multiple(options, value=None, description='', width='80%'):
    if value is None: value = options[0:1]
    return SelectMultiple(
        options=options,
        value=value,
        rows=5,
        description=description,
        disabled=False,
        layout=Layout(width='90%')
    )    

class WidgetCast:
    def __init__(self) -> None:
        """Load info from config files and create a widget to edit the cast."""
        p2games, p2cast, p2prompts = get_paths() 
        self.p2cast = p2cast
        assert self.p2cast.is_file()

        with open(self.p2cast, 'r') as fp:
            lines = fp.readlines()
            cast_names = [line.removesuffix('\n').strip() for line in lines]
        # Create text widget for imputs and button to save
        self.inputs = Text(value=', '.join(cast_names), description='Cast', layout=Layout(width='75%'))
        self.save = create_button(description='save', on_click=self._update_cb)
        
    @property
    def value(self):
        return self.inputs.value

    def update(self, file=None):
        if file is None: 
            p2write = self.p2cast
        else:
            p2write = Path(file) if isinstance(file, str) else file

        with open(p2write, 'w') as fp:
            fp.write(self.inputs.value.replace(', ', '\n'))

    def _update_cb(self, btn):
        self.update()

    def __call__(self):
        self.display()

    def display(self):
        display(self.inputs)
        display(self.save)
   
class WidgetGames:
    def __init__(self) -> None:
        # Load info from config files
        self.p2games, self.p2cast, _ = get_paths()
        assert self.p2games.is_file(), 'not a file'
        with open(self.p2games, 'r') as fp:
            self.games = json.load(fp)

        with open(self.p2cast, 'r') as fp:
            lines = fp.readlines()
            self.cast_names = [line.removesuffix('\n').strip() for line in lines]

        # Build list for each parameter of the games
        self.names = [g['name'] for g in self.games.values()]
        self.nbr_players = [g['nbr_players'] for g in self.games.values()]
        self.nbr_audience = [g['nbr_audience'] for g in self.games.values()]
        self.prompt = [g['prompt'] for g in self.games.values()]
        self.exclude = [g['exclude'] for g in self.games.values()]
        self.host_include = [g['host_include'] for g in self.games.values()]
        self.host_exclude = [g['host_exclude'] for g in self.games.values()]
        self.description = [g['description'] for g in self.games.values()]
        self.tips = [g['tips'] for g in self.games.values()]
        self.ngames = len(self.names)
        self._create_widget_for_game_param()
        self._create_widget_for_game_cast()

    def _create_widget_for_game_param(self):
        # Create widgets to update names and game parameters
        self.w_gnames = [create_text(description='', value=f'{self.names[i]}') for i in range(self.ngames)]
        self.w_nbr_players = [create_text(description= 'Nbr players:  ', value=f'{self.nbr_players[i]}') for i in range(self.ngames)]
        self.w_nbr_audience = [create_text(description='Nbr audience: ', value=f'{self.nbr_audience[i]}') for i in range(self.ngames)]
        self.w_prompt = [create_text(description= 'Prompt:', value=f'{self.prompt[i]}') for i in range(self.ngames)]  
        self.w_descr = [create_text(description= 'Description:', value=f'{self.description[i]}') for i in range(self.ngames)]  
        self.w_tips = [create_text(description= 'Tip:', value=f'{self.tips[i]}') for i in range(self.ngames)]  
        self.save_game_info = create_button(description='save', on_click=self._update_game_info_cb) 

    def _create_widget_for_game_cast(self):
        # Create widgets to update cast related game parameters
        options = ['None'] + self.cast_names
        self.w_exclude = []
        self.w_host_include = []
        self.w_host_exclude = []
        for gexcl, hincl, hexcl in zip(self.exclude, self.host_include, self.host_exclude):
            self.w_exclude.append(create_multiple(options=options, value=gexcl if gexcl else ['None']))
            self.w_host_include.append(create_multiple(options=options, value=hincl if hincl else ['None']))
            self.w_host_exclude.append(create_multiple(options=options, value=hexcl if hexcl else ['None']))
        self.save_game_cast = create_button(description='save', on_click=self._update_game_cast_cb) 

    def _display_game_info(self):
        for i in range(self.ngames):
            display(self.w_gnames[i])
            display(self.w_nbr_players[i])
            display(self.w_nbr_audience[i])
            display(self.w_prompt[i])
            # display(self.w_descr[i])
            # display(self.w_tips[i])
            display(self.save_game_info)    
            display_html('<hr>', raw=True)

    def _display_exclusions(self):
        grid = GridspecLayout(self.ngames+1, 5)
        grid[0,0] = create_label(value='Game name')
        grid[0,1] = create_label(value='Exclude from game')
        grid[0,2] = create_label(value='Include in hosting')
        grid[0,3] = create_label(value='Exclude from hosting')

        for i in range(0, self.ngames):
            grid[i+1, 0] = self.w_gnames[i]
            grid[i+1, 1] = self.w_exclude[i]
            grid[i+1, 2] = self.w_host_include[i]
            grid[i+1, 3] = self.w_host_exclude[i]
            grid[i+1, 4] = create_button(description='save', on_click=self._update_game_cast_cb)

        display(grid)

    def update_game_info(self):
        for i, k in enumerate(self.games.keys()):
            self.games[k]['name'] = self.w_gnames[i].value
            self.games[k]['nbr_players'] = int(self.w_nbr_players[i].value)
            self.games[k]['nbr_audience'] = int(self.w_nbr_audience[i].value)
            self.games[k]['prompt'] = self.w_prompt[i].value

        with open(self.p2games, 'w') as fp:
            json.dump(self.games, fp, indent=4)
    
    def _update_game_info_cb(self, btn):
        self.update_game_info()

    def update_game_cast(self):
 
        def strip_none(l):
            """Takes a tuple or a list and returns a list without the 'None' element"""
            l = l if isinstance(l, list) else list(l)
            if 'None' in l: l.remove('None')
            return l
        
        clean_exclude = [strip_none(w.value) for w in self.w_exclude]
        clean_host_include = [strip_none(w.value) for w in self.w_host_include]
        clean_host_exclude = [strip_none(w.value) for w in self.w_host_exclude]

        for i, k in enumerate(self.games.keys()):
            self.games[k]['exclude'] = clean_exclude[i]
            self.games[k]['host_include'] = clean_host_include[i]
            self.games[k]['host_exclude'] = clean_host_exclude[i]

        with open(self.p2games, 'w') as fp:
            json.dump(self.games, fp, indent=4)
    
    def _update_game_cast_cb(self, btn):
        self.update_game_cast()

    def __call__(self):
        self._display_game_info()
        display_html('<hr>', raw=True)
        self._display_exclusions()

class WidgetPrompts:
    def __init__(self) -> None:
        """Load info from config files and create a widget to edit the prompts."""
        p2games, p2cast, p2prompts = get_paths() 
        self.p2prompts = p2prompts
        assert self.p2prompts.is_file()

        with open(self.p2prompts, 'r') as fp:
            lines = fp.readlines()
            self.prompts = [line.removesuffix('\n').strip() for line in lines]

        self.widgets = []
        for prompt in self.prompts:
            self.widgets.append(Text(value=prompt, description='Prompt', layout=Layout(width='75%')))
        self.save = create_button(description='save', on_click=self._update_cb)
                

    def update(self, file=None):
        if file is None: 
            p2write = self.p2prompts
        else:
            p2write = Path(file) if isinstance(file, str) else file

        with open(p2write, 'w') as fp:
            for widget in self.widgets:
                fp.write(widget.value + '\n')
            # fp.write(self.inputs.value)

    def _update_cb(self, btn):
        self.update()

    def __call__(self):
        self.display()

    def display(self):
        for widget in self.widgets:
            display(widget)
        display(self.save)
 

if __name__ == '__main__':
    setup_logging()
    get_config()
