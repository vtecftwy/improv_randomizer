import sys
import random
import time
import math
import tkinter.messagebox

from pathlib import Path 
from playsound import playsound
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.messagebox import askyesno
from tkinter import *


mm_default = 45
ss_default = 0

ROOT = Path(__file__).resolve().parent

def raw_path(filename:str):
    return rf"{ROOT.absolute().as_posix()}/{filename}"

class GameSpace(object):
    """ Canvas for the game space and prompt boxes"""
    def __init__(self, delay_inc=0.1, delay = 200):
        self.win = tkinter.Tk()
        self.win['background'] = '#000147'
        #win.resizable(False,False)
        self.win.geometry('1920x1080')
        
        self.delay = delay

        self.mm_left = mm_default
        self.ss_left = ss_default

        self.i = 0
        self.x = []
        self.y = []

        self.counter = 0
        self.spin_counter = 0
        self.spinFlag = False
        self.gameslist = []

        # Drawing game screen

        # self.C = Canvas(self.win, bg="#c6f6f2", width=1100, height=700)

        
    def startGame(self):
        self.getPlayers()
        self.getGames()
        self.getPrompts()
        self.start_button['state'] = tkinter.DISABLED
        self.reset_button['state'] = tkinter.NORMAL
        self.spin_button['state'] = tkinter.NORMAL
        self.drawGames()

    def getPlayers(self):
        #Read namelist file and create list
        with open(ROOT/"players.txt", 'r', encoding='UTF-8') as name_file:
            lines = name_file.readlines()
            self.playerlist = [line.strip() for line in lines]

        print(*self.playerlist, sep = "\n")
        print('Players loaded.')

    def getGames(self):
        with open(ROOT/'games.txt', 'r', encoding='UTF-8') as game_file:
            self.gameslist = game_file.readlines()
        
        #Remove line breaks in stopwords list
        for i, line in enumerate(self.gameslist):
            print(i, line)
            self.gameslist[i] = line.strip().split(",")
            print(self.gameslist[i])
            self.gameslist[i][1] = int(self.gameslist[i][1].strip())
            self.gameslist[i][2] = int(self.gameslist[i][2].strip())
            self.gameslist[i][3] = self.gameslist[i][3].replace("\n","")
            self.gameslist[i][3] = self.gameslist[i][3].strip()
            print(self.gameslist[i])
            print('----')

        print(*self.gameslist, sep = "\n")
        print(len(self.gameslist))
        print('Games loaded.')

    def getPrompts(self):
        #Read promptlist file and create list
        with open(ROOT/'prompts.txt', 'r', encoding='UTF-8') as prompt_file:
            lines = prompt_file.readlines()
            self.promptlist = [line.strip() for line in lines]

        print(*self.promptlist, sep='\n')
        print('Prompts loaded.')


    def drawGames(self):
        #split games into areas and figure out positions
        midpt_x = int(self.C.config('width')[4]) / 2
        midpt_y = int(self.C.config('height')[4]) / 2
        position_r=280
        ngames = len(self.gameslist)
        angle = math.radians(360/ngames)
        self.x.clear()
        self.y.clear()
        for i in range(ngames):
            print(angle*i)
            print(math.radians(90))
            if angle*i <= math.radians(90):
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
        f='cyan'
        w, r = 4, 55
        
        #draw game bubbles
        for n, game in enumerate(self.gameslist):
            print(n)
            self.C.create_line(midpt_x, midpt_y, self.x[n], self.y[n], width=w)
            self.C.create_oval(self.x[n]-r-20, self.y[n]-r, self.x[n]+r+20, self.y[n]+r,fill=f)
            self.C.create_text(self.x[n], self.y[n], text=game[0], font=(None,12, 'bold'), width=85)

        #randomise games
        self.rand = list(range(ngames))
        random.shuffle(self.rand)
        print(self.rand)
        print(self.counter)

    def start(self):
        self.win.mainloop()

    def get_timer_string(self):
        return str(self.mm_left).rjust(2,'0') + ':' + str(self.ss_left).rjust(2,'0')

    def update_timer_label(self, fg=None, font=(None,50,'normal')):
        self.timer_label.config(text=self.get_timer_string(),fg=fg, font=font)

    def countdown(self):
        if not self.started:
            return
        else:
            if self.mm_left == 0 and self.ss_left == 1:
                print('OUT OF TIME!')
                self.ss_left = 0
                self.spin_button['state'] = tkinter.DISABLED
                self.update_timer_label(fg='red')
                playsound(raw_path('endhorn.mp3'),False)
                return
            
            elif self.mm_left == 5 and self.ss_left == 1:
                self.ss_left -= 1
                print('FIVE MINUTES LEFT!')
                self.update_timer_label(fg='red', font=(None,50,'bold'))
                playsound(raw_path('ahooga-horn.mp3'),False)

            else:
                if self.ss_left == 0:
                    self.mm_left -= 1
                    self.ss_left=59
                    self.update_timer_label()
                else:
                    self.ss_left -= 1
                    self.update_timer_label()
                    if self.mm_left == 0 and self.ss_left < 31:
                        playsound(raw_path('TickSound.mp3'),False)
                        self.timer_label.config(font=(None,60,'bold'))
        self.win.after(1000,self.countdown)

    def startGame(self):
        self.getPlayers()
        self.getGames()
        self.getPrompts()
        self.start_button['state'] = tkinter.DISABLED
        self.reset_button['state'] = tkinter.NORMAL
        self.spin_button['state'] = tkinter.NORMAL
        self.drawGames()

    def spinGame(self):
        '''global gameslist'''
        # global i
        global spinFlag

        if self.started == False:
            self.started = True
            self.spin_button.config(text='NEXT GAME')
            print(raw_path('Air Horn.mp3'))
            playsound(raw_path('Air Horn.mp3'),False)
            self.countdown()
        
        if self.counter >= len(self.gameslist):
            print('GAME FINISHED! RESET!')
            playsound(raw_path('1up.mp3'),False)
            self.score_label.configure(text='Games Played: '+ str(self.counter))
            self.started = False
            self.spin_button['state'] = tkinter.DISABLED
            r=50
            prev_item = self.rand[self.counter-1]
            self.C.create_oval(self.x[prev_item]-r-20,self.y[prev_item]-r,self.x[prev_item]+r+20,self.y[prev_item]+r,fill='red')
            self.C.create_text(self.x[prev_item], self.y[prev_item], text=self.gameslist[prev_item][0], font=(None,12, 'bold'), width=80)
            self.reset_button.configure(bg='green')

        else:
            if self.counter > 0:
                playsound(raw_path('1up.mp3'),False)
        
            self.score_label.configure(text='Games Played: '+ str(self.counter))
            r=55
            self.spin_counter = self.rand[self.counter]
            prev_item = self.rand[self.counter-1]
            if self.spinFlag == False:
                self.spinFlag = True
            else:
                self.C.create_oval(self.x[prev_item]-r-20,self.y[prev_item]-r,self.x[prev_item]+r+20,self.y[prev_item]+r,fill='red')
                self.C.create_text(self.x[prev_item], self.y[prev_item], text=self.gameslist[prev_item][0], font=(None,12, 'bold'), width=80)
        
            spinbubble = self.C.create_oval(self.x[self.spin_counter]-r-20,self.y[self.spin_counter]-r,self.x[self.spin_counter]+r+20,self.y[self.spin_counter]+r,fill='green2')
            spintext = self.C.create_text(self.x[self.spin_counter], self.y[self.spin_counter], text=self.gameslist[self.spin_counter][0], font=(None,12, 'bold'), width=80)

            next_game = self.gameslist[self.rand[self.counter]][0]
            self.game_label.configure(text=next_game)
            print(next_game)
            
            num_of_players = self.gameslist[self.rand[self.counter]][1] + self.gameslist[self.rand[self.counter]][2]
            next_players = self.playerlist
            if self.counter == 0:
                random.shuffle(next_players)
                self.i = 0
            j = self.i + num_of_players

            if num_of_players == 0:
                self.players_label.configure(text='ALL PLAY')

            elif j == len(next_players):
                random.shuffle(next_players)
                self.i = 0
                j = self.i + num_of_players
                self.players_label.configure(text=f"HOST: {next_players[self.i]}\n{','.join(next_players[self.i+1:j])}")
            elif j > len(next_players):
                print('Exceeded')
                self.i = j - num_of_players
                players_remaining = next_players[self.i:len(next_players)]
                players_needed = num_of_players - len(players_remaining)
                print('Players needed: ' + str(players_needed))
                while players_needed > 0:
                    players_remaining.append('WILDCARD')
                    players_needed -= 1
                print(players_remaining)
                self.players_label.configure(text=f"HOST: {players_remaining[0]}\n{','.join(players_remaining[1:])}")
                random.shuffle(next_players)
                self.i = 0
            else:
                print(next_players[0:num_of_players])
                self.players_label.configure(text=f"HOST: {next_players[self.i]}\n{','.join(next_players[self.i+1:j])}")
                print(next_players)
                print(next_players[self.i:j])
                self.i = j
                
            rand_promptlist = self.promptlist
            random.shuffle(rand_promptlist)

            if self.gameslist[self.rand[self.counter]][0]=='Genres' or self.gameslist[self.rand[self.counter]][0]=='Double Reverse Alphabet' or self.gameslist[self.rand[self.counter]][0]=='Pillars':
                print('Special')
                print(self.gameslist[self.rand[self.counter]][3])
                rand_prompt = rand_promptlist[self.counter]
                next_prompt = self.gameslist[self.rand[self.counter]][3]
                print(rand_prompt)
                self.prompts_label.configure(text=next_prompt+'\n'+'\n'+rand_prompt)
            elif self.gameslist[self.rand[self.counter]][3]=='':
                print('Blank')
                rand_prompt = rand_promptlist[self.counter]
                print(rand_prompt)
                self.prompts_label.configure(text=rand_prompt)
            else:
                print('Text')
                next_prompt = self.gameslist[self.rand[self.counter]][3]
                self.prompts_label.configure(text=next_prompt)
            self.counter += 1
            print(num_of_players)


    def resetGame(self):

        self.start_button['state'] = tkinter.NORMAL
        self.reset_button['state'] = tkinter.DISABLED
        self.spin_button['state'] = tkinter.DISABLED
        self.game_label.configure(text='Game to be played')
        self.players_label.configure(text='Players Chosen')
        self.prompts_label.configure(text='Prompts')
        self.reset_button.configure(bg='SystemButtonFace')
        self.spin_button.config(text='START GAME')
        self.score_label.configure(text='Games Played: 0')
        self.spinFlag = False

        self.started = False
        mm_left = mm_default
        ss_left = ss_default
        time_left = str(mm_left).rjust(2,'0')+':'+str(ss_left).rjust(2,'0')
        self.timer_label.config(text=time_left,fg='black',font=(None,40,'bold'))
        
        self.counter = 0
        self.C.delete('all')
        print('Game RESET!')

    def resetConfirm(self):
        answer = askyesno(title='Hello Dave', message='Are you sure you want to reset?')
        if answer:
            self.resetGame()


if __name__ == '__main__':
    gamespace = GameSpace()
    gamespace.win.title('C.A.R.L.')
    gamespace.start()