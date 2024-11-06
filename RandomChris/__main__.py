import argparse
import logging
import sys
import tkinter as tk
from datetime import datetime, timedelta
from pathlib import Path
from RandomChris.utils import setup_logging

print('Starting ...')
setup_logging()
logging.info(f"\n{'='*50}\nNew Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*50}")

from RandomChris.gamespace import GameSpace
from RandomChris.gamesession import GameSession

# Setup path to package and modules
ROOT = Path(__file__).parent.parent
# sys.path.append(str(ROOT.absolute()))

if __name__ == '__main__':
    
    # Catpure arguments to set priority category, which will overwrite the config.cfg file
    parser = argparse.ArgumentParser(description='Run Improv Randomizer')
    parser.add_argument('--set-category-priority', action='store_true', help='Put selected category in 3rd position')
    parser.add_argument('--category', type=str, default='', help='Category to consider as priority, default is All Play')
    args = parser.parse_args()
    set_priority_category = args.set_category_priority
    priority_category = args.category
    # Pass None to GameSession if the arguments are not set, in order to allow loading values from config.cfg
    if not set_priority_category: set_priority_category = None
    if priority_category == '': priority_category = None
    
    # Main loop   
    session = GameSession(set_priority_category=set_priority_category, priority_category=priority_category)
    window = tk.Tk()
    gamespace = GameSpace(window, session)
    gamespace.draw_games()
    window.mainloop()
        