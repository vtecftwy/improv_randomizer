import logging
import sys
import tkinter as tk
from datetime import datetime, timedelta
from pathlib import Path
from utils import setup_logging

print('Starting ...')
setup_logging()
logging.info(f"\n{'='*50}\nNew Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*50}")

from gamespace import GameSpace
from gamesession import GameSession

# Setup path to package and modules
# TODO: correct this line after transforming this into a package
ROOT = Path(__file__).parent
sys.path.append(str(ROOT.absolute()))
print('root from main', ROOT)

if __name__ == '__main__':
    # Main loop   
    session = GameSession()
    window = tk.Tk()
    gamespace = GameSpace(window, session)
    gamespace.draw_games()
    window.mainloop()
        