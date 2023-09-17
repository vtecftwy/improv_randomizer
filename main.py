import logging
import sys
import tkinter as tk

from datetime import datetime, timedelta
from pathlib import Path
from gamespace import GameSpace
from gamesession import GameSession

# Setup path to package and modules
# TODO: correct this line after transforming this is a package
ROOT = Path(__file__).parent
sys.path.append(str(ROOT.absolute()))

# Setup logging
p2log = ROOT / 'logs/_short.log'
logging.basicConfig(
    filename=p2log, # D:\PyProjects\ai2\short\logs\_short.log
    encoding='utf-8',
    level=logging.INFO,
    # format='%(message)s \n(Module: `%(module)s` Function: `%(funcName)s` line: %(lineno)s)'
    format='%(message)s'
    )
logging.info(f"{'='*50}\nNew Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*50}")


# Main loop
# Create a game session     
session = GameSession()
window = tk.Tk()
gamespace = GameSpace(window, session)
# gamespace.start(session)
gamespace.draw_games()

window.mainloop()




if __name__ == '__main__':
    pass
    