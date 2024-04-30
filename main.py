import sys
import tkinter as tk

from datetime import datetime, timedelta
from pathlib import Path
from gamespace import GameSpace
from gamesession import GameSession
from utils import *

setup_logging()
# Setup path to package and modules
# TODO: correct this line after transforming this into a package
ROOT = Path(__file__).parent
sys.path.append(str(ROOT.absolute()))

if __name__ == '__main__':

    # Main loop   
    session = GameSession()
    window = tk.Tk()
    gamespace = GameSpace(window, session)
    gamespace.draw_games()
    window.mainloop()
        