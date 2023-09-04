import tkinter as tk

from pathlib import Path
from gamespace import GameSpace
from gamesession import GameSession


# Main loop
window = tk.Tk()
gamespace = GameSpace(window)
session = GameSession()
gamespace.update(session)
gamespace.draw_games(session.games)

window.mainloop()




if __name__ == '__main__':

    # session = GameSession()
    # print(len(session.games), session.nbr_games)
    pass
    