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
ORANGE = '#E87257'
PURPLE = '#30293D'
RED = '#8C2A25'
TEST_COLOR = 'pink'
NBR_LINES_IN_INFO = 3


ROOT = Path(__file__).resolve().parent

def raw_path(filename:str):
    return rf"{ROOT.absolute().as_posix()}/assets/audio/{filename}"


class GameSpace:
    """Object representing the game space and all GUI methods"""

    def __init__(self, window) -> None:
        self.spinflag = False
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
        
        print('winfo: w:', window.winfo_screenwidth(), 'h: ',window.winfo_screenheight())

    def build_header(self):
        pass

    def build_footer(self):
        self.score_label = ttk.Label(
            self.footer, text='Number Games Played:   \n', style='Main.TLabel',
            anchor='ne', justify=tk.CENTER, 
            width=30
            )
        self.score_label.grid(row=1, column=1, columnspan=10, sticky='ns')
        
        self.time_left_label = ttk.Label(
            self.footer, text='Time Left: x Min\n', style='Main.TLabel',
            anchor='ne', justify=tk.CENTER, 
            width=40
            )
        self.time_left_label.grid(row=1, column=11, columnspan=10, sticky='ns')

        self.btn_reset = ttk.Button(
            self.footer, text='Reset', command=self.reset, 
            style='Small.TButton')
        self.btn_reset.grid(row=1, column=31, columnspan=5)

    def draw_canvas_bg(self):
        self.img = ImageTk.PhotoImage(Image.open(ROOT/'assets/img/app_bg_1100x700_01.png'))
        self.canvas.create_image(0, 0, anchor='nw', image=self.img)
        print('img info: w:', self.img.width(), 'h:', self.img.height())

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

        self.btn_next = ttk.Button(self.info_fr, text='START', command=self.next_game, style='Main.TButton')
        self.btn_next.grid(row=31, rowspan=1, column=1)

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

    def start(self, session):
        """Start the game, and link the game space and the game session"""
        self.session = session

    def next_game(self):
        # First time the button is pressed
        if self.session.game_started == False:
            self.session.start_game()
            self.btn_next.config(text='NEXT')
            playsound(raw_path('Air Horn.mp3'),False)
            self.countdown()
        # When all game were played
        if self.session.nbr_games_played >= self.nbr_games:
            print('ALL GAMES FINISHED! RESET!')
            playsound(raw_path('1up.mp3'),False)
            self.update_score_lbl(session.nbr_games_played)
            self.session.game_started = False
            self.btn_next['state'] = tk.DISABLED
            r=50
            prev_game = self.session.game_sequence[self.step]
            self.canvas.create_oval(self.x[prev_game]-r-20,self.y[prev_game]-r,self.x[prev_game]+r+20,self.y[prev_game]+r,fill='red')
            self.canvas.create_text(self.x[prev_game], self.y[prev_game], text=self.session.games[prev_game].name, font=(None,12, 'bold'), width=80)
            self.btn_reset.configure(bg='green')
            
        else:
            if session.nbr_games_played > 0:
                session.pick_next_game()

                playsound(raw_path('1up.mp3'),False)
                self.update_score_lbl(session.nbr_games_played)
                # Update current and previous game drawing
                r=55
                cur_game = self.session.current_game_idx 
                prev_game = self.session.previous_game_idx

                if self.spinflag == False:
                    self.spinflag = True
                else:
                    self.canvas.create_oval(
                        self.x[prev_game]-r-20, self.y[prev_game]-r, 
                        self.x[prev_game]+r+20, self.y[prev_game]+r, fill='red'
                        )
                    self.canvas.create_text(
                        self.x[prev_game], self.y[prev_game], 
                        text=self.session.games[prev_game].name, 
                        font=(None,12, 'bold'), width=80
                        )

            # spinbubble = self.C.create_oval(x[spin_counter]-r-20,y[spin_counter]-r,x[spin_counter]+r+20,y[spin_counter]+r,fill='green2')
            # spintext = self.C.create_text(x[spin_counter], y[spin_counter], text=gameslist[spin_counter][0], font=(None,12, 'bold'), width=80)
            #print('Spinner Primed')
            #Update labels
            # self.session.pick_next_game()
            next_game_idx = session.current_game_idx
            self.update_game_info(next_game_idx)
            print(next_game_idx)
            self.update_player_info(next_game_idx)
      
    #   num_of_players = gameslist[rand[counter]][1]+gameslist[rand[counter]][2]
    #   next_players = playerlist
    #   if counter == 0:
    #     random.shuffle(next_players)
    #     i = 0
    #   j = i + num_of_players
    #   #print ('j = ' + str(j))
    #   #print (len(next_players))
    #   if num_of_players == 0:
    #       self.players_label.configure(text='ALL PLAY')
    #   elif j == len(next_players):
    #       random.shuffle(next_players)
    #       i = 0
    #       j = i + num_of_players
    #       self.players_label.configure(text=f"HOST: {next_players[i]}\n{','.join(next_players[i+1:j])}")
    #   elif j > len(next_players):
    #       #print('Exceeded')
    #       i = j - num_of_players
    #       players_remaining = next_players[i:len(next_players)]
    #       players_needed = num_of_players - len(players_remaining)
    #       #print('Players needed: '+str(players_needed))
    #       while players_needed > 0:
    #           players_remaining.append('WILDCARD')
    #           players_needed -= 1
    #       #print(players_remaining)
    #       self.players_label.configure(text=f"HOST: {players_remaining[0]}\n{','.join(players_remaining[1:])}")
    #       random.shuffle(next_players)
    #       i = 0
    #   else:
    #       #print(next_players[0:num_of_players])
    #       self.players_label.configure(text=f"HOST: {next_players[i]}\n{','.join(next_players[i+1:j])}")
    #       #print(next_players)
    #       #print(next_players[i:j])
    #       i = j
            
    #   rand_promptlist = promptlist
    #   random.shuffle(rand_promptlist)
    #   if gameslist[rand[counter]][0]=='Genres' or gameslist[rand[counter]][0]=='Double Reverse Alphabet' or gameslist[rand[counter]][0]=='Pillars':
    #     #print('Special')
    #     print(gameslist[rand[counter]][3])
    #     rand_prompt = rand_promptlist[counter]
    #     next_prompt = gameslist[rand[counter]][3]
    #     #print(rand_prompt)
    #     self.prompts_label.configure(text=next_prompt+'\n'+'\n'+rand_prompt)
    #   elif gameslist[rand[counter]][3]=='':
    #     #print('Blank')
    #     rand_prompt = rand_promptlist[counter]
    #     print(rand_prompt)
    #     self.prompts_label.configure(text=rand_prompt)
    #   else:
    #     #print('Text')
    #     next_prompt = gameslist[rand[counter]][3]
    #     self.prompts_label.configure(text=next_prompt)
    #   counter += 1
    #   #print(num_of_players)

    def countdown(self, t=0):
        """Start a countdown timer"""
        print('Game Space Countdown')
        # start timer, update timer label

    def reset(self):
        pass

    def update_score_lbl(self, n):
        """Update the score label on the game space window"""
        self.score_label.configure(text='Games Played: '+str(n))

    def update_game_info(self, gameidx):
        """Update the game info section on the game space window"""
        game_name = self.session.games[gameidx].name
        print(game_name)
        txt = f"{game_name}\n"
        self.game_info.configure(text=txt)

    def update_player_info(self, gameidx):
        """Update the player info section on the game space window"""
        idxs, players = self.session.pick_players(self.session.games[gameidx])
        print(idxs, players)
        players_txt = f"{', '.join(players)}"
        txt = players_txt + '\n' * (NBR_LINES_IN_INFO - len(players_txt)//28)
        self.players_info.configure(text=txt)


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


if __name__ == '__main__':
    from gamesession import GameSession
    
    window = tk.Tk()
    gamespace = GameSpace(window)
    session = GameSession()
    gamespace.start(session)
    gamespace.draw_games()

    window.mainloop()