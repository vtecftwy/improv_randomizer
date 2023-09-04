import sys
import random
import time
import math
import tkinter as tk
import tkinter.messagebox

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

ROOT = Path(__file__).resolve().parent

def raw_path(filename:str):
    return rf"{ROOT.absolute().as_posix()}/{filename}"

class GameSpace(object):
    """Includes game window, graphics and logic for short forms"""
    def __init__(self, root, delay_inc=0.1, delay = 200):

        # Define styles
        self.s = ttk.Style()
        self.s.configure(
            'Main.TFrame', background=BLUE, 
            relief=tk.NONE, borderwidth=0,
            )
        self.s.configure(
            'Info.TFrame', background=BLUE, 
            relief=tk.NONE, borderwidth=0,
            padding=(50,100)
            )
        self.s.configure(
            'Main.TLabel', background=BLUE, foreground='white', 
            font=(None, 20, 'bold'), 
            relief=tk.NONE
            )
        self.s.configure(
            'Info.TLabel', background=BLUE, foreground='white', 
            font=(None, 20, 'bold'), 
            anchor='w', justify=tk.LEFT,
            relief=tk.NONE, borderwidth=0,
            padding=(10,10)
            )
        
        # Build the game window
        # Window bar = 40px, Window taskbar = 40 px
        root.title(title)
        root.geometry('1920x800')

        # Set frames
        self.header = ttk.Frame(root, width=1900, heigh=40, style='Main.TFrame')
        self.header.grid(row=1, column=1, sticky='we')

        self.header_text = ttk.Label(
            self.header, text='Played Games: ', style='Main.TLabel',
            anchor='center', justify=tk.LEFT, 
            )
        self.header_text.grid(row=1, column=1, columnspan=2, sticky='we')

        self.main = ttk.Frame(root, width=1900, heigh=700, style='Main.TFrame')
        self.main.grid(row=2, column=1, sticky='we')

        self.footer = ttk.Frame(root, width=1900, heigh=60, style='Main.TFrame')
        self.footer.grid(row=3, column=1, sticky='ns')

        # Create canvas in main frame
        self.canvas = tk.Canvas(self.main, width=1100, height=700, borderwidth=0, highlightthickness=0) 
        self.canvas.grid(row=1, column=1, columnspan=10, sticky='nw')
        self.draw_canvas()
        self.build_info_columns()
        # print(root.winfo_screenwidth(), root.winfo_screenheight())

        
    def draw_canvas(self):
        self.img = ImageTk.PhotoImage(Image.open(ROOT/'assets/img/app_bg_1100x700_01.png'))
        print(self.img.width(), self.img.height())
        self.canvas.create_image(0, 0, anchor='nw', image=self.img)

        # self.canvas.create_text(10, 1, text='TEST1', anchor='nw', font='TkMenuFont', fill='white')
        # self.canvas.create_text(10, 100, text='TEST2', anchor='nw', font='TkMenuFont', fill='white')

    def build_info_columns(self):   
        # Create Info Frame
        # self.info = ttk.Frame(self.main, width=800, style='Main.TFrame')
        self.info = ttk.Frame(self.main, style='Info.TFrame')
        self.info.grid(row=1, column=11, sticky='nesw')

        self.game_info = ttk.Label(
            self.info, text='Game name:\n\n.', style='Info.TLabel'
            )
        self.game_info.grid(row=1, rowspan=10, column=1, sticky='we')
        
        self.player_info = ttk.Label(
            self.info, text='Player names: \n \n \n.', style='Info.TLabel'
            )
        self.player_info.grid(row=11, rowspan=10, column=1, sticky='we')

        self.prompt_info = ttk.Label(
            self.info, text='Prompt: \n \n \n.', style='Info.TLabel'
            )
        self.prompt_info.grid(row=21, rowspan=10, column=1, sticky='we')

    def draw_games(self):
        #split games into areas and figure out positions
        midpt_x = int(self.C.config('width')[4]) / 2
        midpt_y = int(self.C.config('height')[4]) / 2
        position_r=280
        #C.create_text(midpt_x, midpt_y, text='Center', font=(None,12))
        angle = math.radians(360/len(gameslist))
        #print(angle)
        n_games = len(gameslist) - 1
        x.clear()
        y.clear()
        
if __name__ == '__main__':
    root = tk.Tk()
    gamespace = GameSpace(root)
    root.mainloop()