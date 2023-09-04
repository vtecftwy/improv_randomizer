import math
import random
import tkinter as tk

from pathlib import Path 
from PIL import ImageTk, Image
from playsound import playsound
from pprint import pprint
from tkinter import ttk
from tkinter.messagebox import askyesno

# Define game parameters
mm_default = 45
ss_default = 0
title = 'C.A.R.L.'
BLUE = '#0B404E'
CYAN = '#15EAEB'
RED = 'red'
TEST_COLOR = 'pink'


ROOT = Path(__file__).resolve().parent

def raw_path(filename:str):
    return rf"{ROOT.absolute().as_posix()}/assets/audio/{filename}"


class GameSpace:
    """Object representing the game space and all GUI methods"""

    def __init__(self, window) -> None:
        self.define_styles()
        self.build_layout(window)
        self.build_header()
        self.draw_canvas_bg()
        self.build_info_columns()
        self.build_footer()
        print('GameSpace created')

    def define_styles(self):
        # Define styles
        self.s = ttk.Style()
        self.s.configure(
            'Main.TFrame', background=BLUE, 
            relief=tk.NONE, borderwidth=0,
            )
        self.s.configure(
            'Red.TFrame', background=RED, 
            relief=tk.NONE, borderwidth=0,
            )
        self.s.configure(
            'Info.TFrame', background=BLUE, 
            relief=tk.NONE, borderwidth=0,
            padding=(5,5)
            )
        self.s.configure(
            'Main.TLabel', background=BLUE, foreground='white', 
            font=(None, 20, 'bold'), 
            relief=tk.NONE
            )
        self.s.configure(
            'Info.TLabel', background=BLUE, foreground='white', 
            font=(None, 20, 'bold'), 
            width=28,
            anchor='w', justify=tk.LEFT,
            # relief=tk.GROOVE , borderwidth=0,
            relief=tk.NONE , borderwidth=0,
            padding=(5,5)
            )
        self.s.configure(
            'Main.TButton', background=CYAN, foreground='black',
            font=(None, 30, 'bold'), 
            width=10,
            anchor='we', 
            justify=tk.CENTER,
            )
        
    def build_layout(self, window):
        """Build the game window, with empty canvas, and info frames"""

        # Format the game window (Window bar=40px, Windows taskbar = 40 px)
        window.title(title)
        window.configure(background=BLUE)
        window.geometry('1920x1080')

        # Set frames
        self.header = ttk.Frame(window, width=1900, heigh=40, style='Main.TFrame')
        self.header.grid(row=1, column=1, sticky='we')

        # self.header_text = ttk.Label(
        #     self.header, text='Played Games: ', style='Main.TLabel',
        #     anchor='center', justify=tk.LEFT, 
        #     )
        # self.header_text.grid(row=1, column=1, columnspan=2, sticky='we')

        self.main = ttk.Frame(window, width=1900, heigh=700, style='Main.TFrame')
        self.main.grid(row=2, column=1, sticky='we')

        self.footer = ttk.Frame(window, width=1900, heigh=40, style='Main.TFrame')
        self.footer.grid(row=3, column=1, sticky='we')

        # Create canvas in main frame
        self.canvas = tk.Canvas(self.main, width=1100, height=700, borderwidth=0, highlightthickness=0) 
        self.canvas.grid(row=1, column=1, columnspan=10, sticky='nw')
        
        print('winfo: w:', window.winfo_screenwidth(), 'h: ',window.winfo_screenheight())

    def build_header(self):
        pass

    def build_footer(self):
        self.footer_text_1 = ttk.Label(
            self.footer, text='\nPlayed Games: n.   \n', style='Main.TLabel',
            anchor='center', justify=tk.LEFT, 
            width=40
            )
        self.footer_text_1.grid(row=1, column=1, sticky='ns')
        
        self.footer_text_2 = ttk.Label(
            self.footer, text='\nTime Left: x Min\n', style='Main.TLabel',
            anchor='center', justify=tk.LEFT, 
            width=40
            )
        self.footer_text_2.grid(row=1, column=3, sticky='ns')

        self.btn_load = ttk.Button(self.footer, text='Load', command=self.next_game, style='Main.TButton')
        self.btn_load.grid(row=1, column=5)

    def draw_canvas_bg(self):
        self.img = ImageTk.PhotoImage(Image.open(ROOT/'assets/img/app_bg_1100x700_01.png'))
        self.canvas.create_image(0, 0, anchor='nw', image=self.img)
        print('img info: w:', self.img.width(), 'h:', self.img.height())

    def build_info_columns(self):   
        # Create Info Frame
        # self.info_fr = ttk.Frame(self.main, width=800, style='Main.TFrame')
        self.info_fr = ttk.Frame(self.main, style='Info.TFrame')
        self.info_fr.grid(row=1, column=11, sticky='nesw')

        self.game_info = ttk.Label(
            self.info_fr, text='Game name:\n\n\n\n\n', style='Info.TLabel'
            )
        self.game_info.grid(row=1, rowspan=10, column=1, sticky='we')
        
        self.players_info = ttk.Label(
            self.info_fr, text='Players:\n\n\n\n\n', style='Info.TLabel'
            )
        self.players_info.grid(row=11, rowspan=10, column=1, sticky='we')

        self.prompt_info = ttk.Label(
            self.info_fr, text='Prompt:\n\n\n\n\n', style='Info.TLabel'
            )
        self.prompt_info.grid(row=21, rowspan=10, column=1, sticky='we')

        self.btn_next = ttk.Button(self.info_fr, text='START', command=self.next_game, style='Main.TButton')
        self.btn_next.grid(row=31, rowspan=1, column=1)

    def draw_games(self, games):
        self.x = []
        self.y = []
        self.nbr_games = len(games)
        #split games into areas and figure out positions
        midpt_x = int(self.canvas.config('width')[4]) / 2
        midpt_y = int(self.canvas.config('height')[4]) / 2
        position_r=280
        # self.canvas.create_text(midpt_x, midpt_y, text='Center', font=(None,12))
        angle = math.radians(360/self.nbr_games)
        print(angle)
        n_games = self.nbr_games - 1
        self.x.clear()
        self.y.clear()
        for i in range(0, self.nbr_games):
            print(angle*i)
            print(math.radians(90))
            if angle * i <= math.radians(90):
                self.x.append(midpt_x+position_r*math.sin(angle*i)*1.5)
                self.y.append(midpt_y-position_r*math.cos(angle*i))
            elif angle*i <= math.radians(180):
                self.x.append(midpt_x+position_r*math.cos(angle*i-math.radians(90))*1.5)
                self.y.append(midpt_y+position_r*math.sin(angle*i-math.radians(90)))
            elif angle*i <= math.radians(270):
                self.x.append(midpt_x-position_r*math.sin(angle*i-math.radians(180))*1.5)
                self.y.append(midpt_y+position_r*math.cos(angle*i-math.radians(180)))
            elif angle*i < math.radians(360):
                self.x.append(midpt_x-position_r*math.cos(angle*i-math.radians(270))*1.5)
                self.y.append(midpt_y-position_r*math.sin(angle*i-math.radians(270)))
            else:
                print('Something bad happened.')
        #C.create_text(x[i], y[i], text=gameslist[i][0], font=(None,12))
        print(self.x[i])
        print(self.y[i])

        f = CYAN
        o = BLUE
        w = 1
        r = 55
        
        #draw game bubbles
        for n in range(0,n_games+1):
            self.canvas.create_line(midpt_x,midpt_y,self.x[n],self.y[n],width=w, fill=f)
            self.canvas.create_oval(
                self.x[n]-r-20, self.y[n]-r, self.x[n] + r + 20, self.y[n]+r,
                fill=f, outline=o, width=w)
            self.canvas.create_text(
                self.x[n], self.y[n], text=games[n].name, 
                font=(None,12, 'bold'), 
                width=85, justify=tk.CENTER, anchor='center')

        #randomise games
        rand = list(range(len(games)))
        random.shuffle(rand)
        print(rand)

    def next_game(self):
        """Start the next game"""
        pass

    def update(self, session):
        """Update the game space window"""
        self.session = session
        print('Game Space Draw')
        # update canvas, update info sections, update buttons

    def reset(self):
        """Reset the game space"""
        self.build()
        print('Game Space Reset')

    def post_game_info(self, gameid):
        """Post info on game in the info section"""
        print('Game Space Post Game Info')

    def spin_games(self, gameid, nbr_full_spins=4):
        """Spin the around the games nbr_full_spins times then stop on gameid"""
        print('Game Space Spin Games')

    def next_game(self):
        """Pick the next game and players and display them"""
        print('Game Space Next Game')

if __name__ == '__main__':
    from gamesession import GameSession
    
    window = tk.Tk()
    gamespace = GameSpace(window)
    session = GameSession()
    gamespace.update(session)
    gamespace.draw_games(session.games)

    window.mainloop()