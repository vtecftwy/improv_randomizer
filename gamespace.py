import math
import random
import tkinter as tk

from datetime import datetime, timedelta
from pathlib import Path 
from PIL import ImageTk, Image
from playsound import playsound
from pprint import pprint
from tkinter import ttk
from tkinter.messagebox import askyesno
from utils import *

# Define game parameters
mm_default = 45
ss_default = 0
title = 'C.A.R.L.'
BLUE = '#0B404E'
CYAN = '#15EAEB'
DARK_GREEN = '#04282B'
GREEN = '#056F70'
LIGHT_GREEN = '#39C5BD'
ORANGE = '#AF3841'
PURPLE = '#30293D'
RED = '#8C2A25'
TEST_COLOR = 'pink'
WHITE = '#F2F2F2'
NBR_LINES_IN_INFO = 3


ROOT = Path(__file__).resolve().parent

def raw_path(filename:str):
    return rf"{ROOT.absolute().as_posix()}/assets/audio/{filename}"


class GameSpace:
    """Handles all GUI aspects of the game session:

    - Build the game space in the passed window (frames, canvas, labels, buttons, etc.)
    - Callbacks for all buttons

    It does not handle any logic of the game or the handling of the game session state.
    It access this information throught the passed instance of GameSession and by calling its methods.
    """

    @monitor_fn
    def __init__(self, window, session) -> None:
        logthis(f"   Creating new GameSpace object")
        self.window = window
        self.spinflag = False # TODO: what role does this flag play?
        self.session = session

        self.define_styles()
        self.build_layout(window)
        self.build_header()
        self.draw_canvas_bg()
        self.build_info_columns()
        self.build_footer()
        logthis('   GameSpace created')

    @monitor_fn
    def define_styles(self):
        # Define styles
        self.s = ttk.Style()
        # Frames
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
            # padding=(5,5)
            )
        # Labels
        self.s.configure(
            'Main.TLabel', background=BLUE, foreground='white', 
            font=(None, 20, 'bold'), 
            relief=tk.NONE
            )
        self.s.configure(
            'Info.TLabel', background=BLUE, foreground='white', 
            font=(None, 20, 'normal'), 
            width=25,
            wraplength=350,
            anchor='center', justify=tk.CENTER,
            # relief=tk.GROOVE , borderwidth=1,
            relief=tk.NONE , borderwidth=0,
            # padding=(5,5)
            )
        self.s.configure(
            'Header.TLabel', background=BLUE, foreground='white', 
            font=(None, 20, 'bold'), 
            # width=25, 
            anchor='we', justify=tk.CENTER,
            # relief=tk.GROOVE , borderwidth=1,
            relief=tk.NONE , borderwidth=0,
            # padding=(5,5)
            )
        self.s.configure(
            'GameName.TLabel', background=BLUE, foreground=CYAN, 
            font=(None, 24, 'bold'), 
            # width=25, 
            anchor='center', justify=tk.CENTER,
            # relief=tk.GROOVE , borderwidth=1,
            relief=tk.NONE , borderwidth=0,
            # padding=(5,5)
            )
        # Buttons
        self.s.configure(
            'Main.TButton', background=CYAN, foreground='black',
            font=(None, 30, 'bold'), 
            width=10,
            anchor='center', 
            justify=tk.CENTER,
            )
        self.s.configure(
            'Small.TButton', background=CYAN, foreground='black',
            font=(None, 15, 'normal'), 
            width=6,
            anchor='center', 
            justify=tk.CENTER,
            )

    @monitor_fn
    def build_layout(self, window):
        """Build the game window, with empty canvas, and info frames"""

        # Format the game window (Window bar=40px, Windows taskbar = 40 px)
        window.title(title)
        window.configure(background=BLUE)
        window.geometry('1920x1080')

        # Set frames
        self.header = ttk.Frame(window, width=1900, heigh=20, style='Main.TFrame')
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
        
        logthis('   winfo: w:', window.winfo_screenwidth(), 'h: ',window.winfo_screenheight())

    @monitor_fn
    def build_header(self):
        pass

    @monitor_fn
    def build_footer(self):
        self.score_label = ttk.Label(
            self.footer, text='Number Games Played: 0\n', style='Main.TLabel',
            anchor='ne', justify=tk.CENTER, 
            width=30
            )
        self.score_label.grid(row=1, column=1, columnspan=10, sticky='ns')
        
        self.time_left_label = ttk.Label(
            self.footer, text='Time Left: x:xx:xx\n', style='Main.TLabel',
            anchor='ne', justify=tk.CENTER, 
            width=40
            )
        self.time_left_label.grid(row=1, column=11, columnspan=10, sticky='ns')

        # self.btn_reset = ttk.Button(
        #     self.footer, text='Reset', command=self.reset, 
        #     style='Small.TButton')
        # self.btn_reset.grid(row=1, column=31, columnspan=5)

    @monitor_fn
    def draw_canvas_bg(self):
        self.img = ImageTk.PhotoImage(Image.open(ROOT/'assets/img/app_bg_1100x700_01.png'))
        self.canvas.create_image(0, 0, anchor='nw', image=self.img)
        logthis('   img info: w:', self.img.width(), 'h:', self.img.height())

    @monitor_fn
    def build_info_columns(self):   
        # Create Info Frame

        self.info_fr = ttk.Frame(self.main, style='Info.TFrame')
        self.info_fr.grid(row=1, column=11, sticky='nesw')

        # self.game_info_header = ttk.Label(
        #     self.info_fr, text='Game name:', style='Header.TLabel'
        #     )
        # self.game_info_header.grid(row=1, rowspan=1, column=1, sticky='we')
        self.game_info = ttk.Label(
            self.info_fr, text='Game to play\n', style='GameName.TLabel'
            )
        self.game_info.grid(row=2, rowspan=1, column=1, sticky='we')
        
        self.players_info_header = ttk.Label(
            self.info_fr, text='Players:', style='Header.TLabel'
            )
        self.players_info_header.grid(row=11, rowspan=1, column=1, sticky='we')
        self.players_info = ttk.Label(
            self.info_fr, text='\n' * NBR_LINES_IN_INFO, style='Info.TLabel'
            )
        self.players_info.grid(row=12, rowspan=9, column=1, sticky='we')

        self.prompt_info_header = ttk.Label(
            self.info_fr, text='Prompt:', style='Header.TLabel'
            )
        self.prompt_info_header.grid(row=21, rowspan=1, column=1, sticky='we')
        self.prompt_info = ttk.Label(
            self.info_fr, text='\n' * NBR_LINES_IN_INFO, style='Info.TLabel'
            )
        self.prompt_info.grid(row=22, rowspan=9, column=1, sticky='we')

        self.btn_next = ttk.Button(self.info_fr, text='START', command=self.click_next, style='Main.TButton')
        self.btn_next.grid(row=31, rowspan=1, column=1)

    @monitor_fn
    def draw_games(self):
        games = self.session.games
        self.x = []
        self.y = []
        self.nbr_games = len(games)
        #split games into areas and figure out positions
        midpt_x = int(self.canvas.config('width')[4]) / 2
        midpt_y = int(self.canvas.config('height')[4]) / 2
        position_r=280
        # self.canvas.create_text(midpt_x, midpt_y, text='Center', font=(None,12))
        angle = math.radians(360/self.nbr_games)
        # logthis(angle)
        n_games = self.nbr_games - 1
        self.x.clear()
        self.y.clear()
        for i in range(0, self.nbr_games):
            # logthis(angle*i)
            # logthis(math.radians(90))
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
                logthis('   Something bad happened.')
        #C.create_text(x[i], y[i], text=gameslist[i][0], font=(None,12))
        # logthis(self.x[i])
        # logthis(self.y[i])

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

    @monitor_fn
    def click_next(self):
        """Calls session.pick_next_game() and update GUI accordingly to new state
        
        1. Update GameSpace assets when required (e.g. START to NEXT)
        2. Pick next game
        3. Update info on GameSpace (all info comes from self.session):
            - Game Name
            - Players
            - Prompt
            - Score, nbr of games played, time left, ...
        """
        logthis(f"   step: {self.session.step} curr: {self.session.current_game_idx}, prev: {self.session.previous_game_idx}")
        # First time the button is pressed:
        if self.session.session_started == False:
            logthis(f"   Session not started yet (session_started = {self.session.session_started})")
            self.btn_next.config(text='NEXT')
            sound_to_play = 'Air Horn.mp3'
            playsound(raw_path(sound_to_play),False)
    
        # When all game were played
        elif self.session.step >= self.nbr_games:
            logthis(f"   All Games Played (nbr played: {self.session.nbr_games_played})! RESET!")
            self.btn_next['state'] = tk.DISABLED
            sound_to_play = '1up.mp3'
            playsound(raw_path(sound_to_play),False)

        # Active session with games to be played
        else:
            logthis(f"   Ongoing session, nbr played: {self.session.nbr_games_played}")
            sound_to_play = '1up.mp3'
            playsound(raw_path(sound_to_play),False)

        self.session.pick_next_game()
        self.mark_game_complete()
        self.mark_game_current()
        self.countdown() 
        # FIXME countdown should be in first test clause above, but at that moment, start_time is not set yet  

        if self.session.current_game_idx is not None:
            gameidx = self.session.current_game_idx
            self.update_game_info(gameidx)
            self.update_player_info(gameidx)

    @monitor_fn
    def mark_game_complete(self):
        """Mark previous game as complete"""
        idx = self.session.previous_game_idx
        logthis(f"   Marking game {idx} as complete")
        if idx is None:
            return
        else:
            r=55
            self.canvas.create_oval(
                self.x[idx]-r-20, self.y[idx]-r, 
                self.x[idx]+r+20, self.y[idx]+r, fill=DARK_GREEN
                )
            self.canvas.create_text(
                self.x[idx], self.y[idx], 
                text=self.session.games[idx].name, 
                font=(None,12, 'bold'), width=80,
                fill=LIGHT_GREEN
                )

    @monitor_fn
    def mark_game_current(self):
        """Mark current game as active"""
        idx = self.session.current_game_idx
        logthis(f"   Marking game {idx} as complete")
        if idx is None:
            return
        else:
            r=55
            self.canvas.create_oval(
                self.x[idx]-r-20, self.y[idx]-r, 
                self.x[idx]+r+20, self.y[idx]+r, 
                fill=ORANGE
                )
            self.canvas.create_text(
                self.x[idx], self.y[idx], 
                text=self.session.games[idx].name, 
                font=(None,12, 'bold'), width=80,
                fill=WHITE
                )

    def countdown(self, t=0):
        """Update timer label and signal 5 min and 1 min with alarm, red color and clock ticks"""
        timeleft = self.session.time_left
        self.time_left_label.configure(text=f"Time Left: {self.hr_min_sec(timeleft)}")
        # Sound alarm at 5 minutes left
        if timedelta(seconds=60*5) <= timeleft <= timedelta(seconds=60*5+59):
            playsound(raw_path('ahooga-horn.mp3'),False)
        # Red timer and clock ticks from 60 seconds on
        if timeleft <= timedelta(seconds=60):
            self.time_left_label.configure(foreground = 'red')
            playsound(raw_path('TickSound.mp3'),False)
        self.window.after(1000,self.countdown)

    @staticmethod
    def hr_min_sec(td):
        """Convert a timedelta object to a string of the form HH:MM:SS"""
        return str(td).split('.')[0]
    
    @monitor_fn
    def reset(self):
        raise NotImplementedError('GameSpace.reset() not implemented')

    @monitor_fn
    def update_score_lbl(self, n):
        """Update the score label on the game space window"""
        self.score_label.configure(text='Games Played: ' + str(n))

    @monitor_fn
    def update_game_info(self, gameidx):
        """Update the game info section on the game space window"""
        game_name = self.session.games[gameidx].name
        logthis(f"  update info for gameidx: {gameidx} and name {game_name}")
        txt = f"{game_name}\n"
        self.game_info.configure(text=txt)
        
        self.prompt_info.configure(text=self.game_prompt(gameidx))
        
        self.score_label.configure(text='Number Games Played: ' + str(self.session.nbr_games_played) + '\n')

    @monitor_fn
    def game_prompt(self, gameidx):
        """Return a random prompt from the list of prompts"""
        prompt = getattr(self.session.games[gameidx], 'prompt', None)
        prompt = prompt if prompt is not None else random.choice(self.session.promptlist)
        return prompt + '\n'*3  if len(prompt) < 23 else prompt + '\n'*2 

    @monitor_fn
    def update_player_info(self, gameidx):
        """Update the player info section on the game space window"""
        idxs, players = self.session.pick_players(self.session.games[gameidx])
        logthis(f"   player idxs: {idxs}, players: {players}")
        players_txt = f"{', '.join(players)}"
        txt = players_txt + '\n' * (NBR_LINES_IN_INFO - len(players_txt)//28)
        self.players_info.configure(text=txt)

    @monitor_fn
    def post_game_info(self, gameid):
        """Post info on game in the info section"""
        raise NotImplementedError('GameSpace.post_game_info() not implemented')

    @monitor_fn
    def spin_games(self, gameid, nbr_full_spins=4):
        """Spin the around the games nbr_full_spins times then stop on gameid"""
        raise NotImplementedError('GameSpace.spin_games() not implemented')


if __name__ == '__main__':
    from gamesession import GameSession
    
    window = tk.Tk()
    session = GameSession()
    gamespace = GameSpace(window, session)
    # gamespace.start(session)
    gamespace.draw_games()

    window.mainloop()

    window.mainloop()