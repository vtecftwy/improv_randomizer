#=======================INITIALISATION=======================#
import sys
import random
import time
import math
import tkinter.messagebox
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.messagebox import askyesno
from tkinter import *
from playsound import playsound

gameslist = []
playerlist = []
promptlist = []
rand = []
counter = 0
spin_counter = 0
x = []
y = []
mm_default = 45
ss_default = 0
mm_left = mm_default
ss_left = ss_default
spinFlag = False

#========================GUI CODE=======================#
class GameSpace(object):
  # Canvas for the game space and prompt boxes
  def __init__(self, delay_inc=0.1, delay = 200):
    self.win = tkinter.Tk()
    self.delay = delay
    self.win['background'] = '#000147'
    #win.resizable(False,False)
    self.win.geometry('1700x950+50+50')

    '''self.title_label=Label(self.win,text='C.A.R.L', font=(None, 16, 'bold'))
    self.title_label.grid(row=0,columnspan=2)'''

    #Drawing word map
    self.C = Canvas(self.win, bg="#c6f6f2", width=1100, height=700)
    self.C.grid(row=1,rowspan=3,column=0)

    #game_name=Frame(win,bg='red',width=400,height=180,bd=10,relief='ridge')
    #game_name.grid(row=1,column=1)
    self.game_label=Label(self.win,width=30,height=6,text='Game to be played',font=(None, 20, 'bold'),background='#000147', foreground='#4fe3d7',bd=10,relief='ridge',anchor=W)
    self.game_label.grid(row=1,column=1,columnspan=2)

    self.players_label=Label(self.win,width=30,height=6,text='Players Chosen',font=(None, 20, 'bold'),background='#000147', foreground='#4fe3d7',bd=10,relief='ridge',anchor=W,wraplength=500,justify=LEFT)
    self.players_label.grid(row=2,column=1,columnspan=2)

    self.prompts_label=Label(self.win,width=30,height=6,text='Prompts',font=(None, 20, 'bold'),background='#000147', foreground='#4fe3d7',bd=10,relief='ridge',anchor=W,wraplength=500,justify=LEFT)
    self.prompts_label.grid(row=3,column=1,columnspan=2)

    self.start_button=Button(self.win,text='LOAD GAMES', width = 15, height = 2,font=(None, 15, 'bold'), command=self.startGame,background='#000147', foreground='#4fe3d7',activebackground='#4fe3d7',activeforeground='#000147')
    self.start_button.grid(row=4,column=0)

    self.reset_button=Button(self.win,text='RESET', width = 15, height = 2,font=(None, 15, 'bold'), command=self.resetConfirm,state=tkinter.DISABLED, background='#000147', foreground='#4fe3d7',activebackground='#4fe3d7',activeforeground='#000147')
    self.reset_button.grid(row=5,column=0)

    self.spin_button=Button(self.win,text='START GAME', width = 15, height = 2,font=(None, 20, 'bold' ), command=self.spinGame,state=tkinter.DISABLED,background='#000147', foreground='#4fe3d7',activebackground='#4fe3d7',activeforeground='#000147')
    self.spin_button.grid(row=4, rowspan=2, column=1)
    self.started = False

    '''self.paused = True
    self.go_button = Button(self.win, text="Start", command=self.toggle_running)
    self.go_button.grid(row=5,column=1)'''

    self.timer_label=Label(self.win,text=str(mm_left).rjust(2,'0')+':'+str(ss_left).rjust(2,'0'),font=(None,40,'bold'),background='#000147', foreground='#4fe3d7')
    self.timer_label.grid(row=6,column=1)

    self.score_label=Label(self.win,text='Games Played: 0',font=(None,20,'bold'),anchor=W,justify=LEFT,background='#000147', foreground='#4fe3d7')
    self.score_label.grid(row=0,columnspan=2)

  '''def toggle_running(self):
    self.paused = not self.paused
    print(self.paused)
    text = "Start" if self.paused else "Pause"
    self.go_button.config(text=text)
    if not self.paused:
      self.countdown()'''

  def countdown(self):
    global mm_left
    global ss_left
    if not self.started:
      return
    else:
      if mm_left == 0 and ss_left == 1:
        print('OUT OF TIME!')
        ss_left = 0
        #self.go_button['state'] = tkinter.DISABLED
        self.spin_button['state'] = tkinter.DISABLED
        #self.title_label.config(text='C.A.R.L OFFLINE',fg='red')
        time_left = str(mm_left).rjust(2,'0')+':'+str(ss_left).rjust(2,'0')
        self.timer_label.config(text=time_left,fg='red')
        playsound(r'C:\Users\pbarr\Desktop\improv_dev\MonolougeBot-main\endhorn.mp3',False)
        return
      elif mm_left == 5 and ss_left == 1:
        ss_left -= 1
        #print(str(mm_left)+':'+str(ss_left))
        print('FIVE MINUTES LEFT!')
        time_left = str(mm_left).rjust(2,'0')+':'+str(ss_left).rjust(2,'0')
        self.timer_label.config(text=time_left,fg='red',font=(None,50,'bold'))
        playsound(r'C:\Users\pbarr\Desktop\improv_dev\MonolougeBot-main\ahooga-horn.mp3',False)
      else:
        if ss_left == 0:
          mm_left -= 1
          ss_left=59
          #print(str(mm_left)+':'+str(ss_left))
          time_left = str(mm_left).rjust(2,'0')+':'+str(ss_left).rjust(2,'0')
          self.timer_label.config(text=time_left)
        else:
          ss_left -= 1
          #print(str(mm_left)+':'+str(ss_left))
          time_left = str(mm_left).rjust(2,'0')+':'+str(ss_left).rjust(2,'0')
          self.timer_label.config(text=time_left)
          if mm_left == 0 and ss_left < 31:
            playsound(r'C:\Users\pbarr\Desktop\improv_dev\MonolougeBot-main\TickSound.mp3',False)
            self.timer_label.config(font=(None,60,'bold'))
    self.win.after(1000,self.countdown)
      

  def print_games(self):
    print(self.bubbles)

  def spinfirst(self):
    print('First Spin')
    self.spinnext(self.delay)

  def spinnext(self,delay):
    if delay <= 500:
      print('Spin step:'+str(delay))
      delay += 10
      self.win.after(1000,self.spinnext(delay))
    else:
      print('Spinner stopped')
  

  #=======================GAME LOADER=====================#
  def startGame(self):
    self.getPlayers()
    self.getGames()
    self.getPrompts()
    #self.print_games()
    #self.title_label.config(text='C.A.R.L ONLINE',fg='green')
    self.start_button['state'] = tkinter.DISABLED
    self.reset_button['state'] = tkinter.NORMAL
    self.spin_button['state'] = tkinter.NORMAL
    self.drawGames()

  #========================GET PLAYERS=======================#
  def getPlayers(self):
    global playerlist
    #Read namelist file and create list
    name_file = open(r"C:\Users\pbarr\Desktop\improv_dev\MonolougeBot-main\players.txt", 'r', encoding='UTF-8')
    playerlist = name_file.readlines()
    
    #Remove line breaks in stopwords list
    i = 0
    for line in playerlist:
      playerlist[i] = line.strip()
      i += 1

    name_file.close()

    #print(*playerlist, sep = "\n")
    print('Players loaded.')


  #========================GET GAMES=======================#
  def getGames(self):
    global gameslist
    #Read gamelist file and create list
    game_file = open(r'C:\Users\pbarr\Desktop\improv_dev\MonolougeBot-main\games.txt', 'r', encoding='UTF-8')
    gameslist = game_file.readlines()
    
    #Remove line breaks in stopwords list
    i = 0
    for line in gameslist:
      gameslist[i] = line.strip()
      gameslist[i] = line.split(",")
      gameslist[i][1] = int(gameslist[i][1].strip())
      gameslist[i][2] = int(gameslist[i][2].strip())
      gameslist[i][3] = gameslist[i][3].replace("\n","")
      gameslist[i][3] = gameslist[i][3].strip()
      #print(gameslist[i])
      i += 1

    game_file.close()

    #List of all games
    self.bubbles = gameslist

    #print(*gameslist, sep = "\n")
    #print(len(gameslist))
    print('Games loaded.')


  #========================GET PROMPTS====================#
  def getPrompts(self):
    global promptlist
    #Read promptlist file and create list
    prompt_file = open(r'C:\Users\pbarr\Desktop\improv_dev\MonolougeBot-main\prompts.txt', 'r', encoding='UTF-8')
    promptlist = prompt_file.readlines()
    
    #Remove line breaks in stopwords list
    i = 0
    for line in promptlist:
      promptlist[i] = line.strip()
      i += 1

    prompt_file.close()

    #print(promptlist)
    print('Prompts loaded.')

  #===================DRAW GAMES========================#
  def drawGames(self):
    global gameslist
    global rand
    global counter
    global x
    global y
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
    for i in range(0,n_games+1):
      #print(angle*i)
      #print(math.radians(90))
      if angle*i <= math.radians(90):
        x.append(midpt_x+position_r*math.sin(angle*i)*1.5)
        y.append(midpt_y-position_r*math.cos(angle*i))
      elif angle*i <= math.radians(180):
        x.append(midpt_x+position_r*math.cos(angle*i-math.radians(90))*1.5)
        y.append(midpt_y+position_r*math.sin(angle*i-math.radians(90)))
      elif angle*i <= math.radians(270):
        x.append(midpt_x-position_r*math.sin(angle*i-math.radians(180))*1.5)
        y.append(midpt_y+position_r*math.cos(angle*i-math.radians(180)))
      elif angle*i < math.radians(360):
        x.append(midpt_x-position_r*math.cos(angle*i-math.radians(270))*1.5)
        y.append(midpt_y-position_r*math.sin(angle*i-math.radians(270)))
      else:
        print('Something bad happened.')
      #C.create_text(x[i], y[i], text=gameslist[i][0], font=(None,12))
      #print(x[i])
      #print(y[i])

    f='cyan'
    w=4
    r=55
    
    #draw game bubbles
    for n in range(0,n_games+1):
      self.C.create_line(midpt_x,midpt_y,x[n],y[n],width=w)
      self.C.create_oval(x[n]-r-20,y[n]-r,x[n]+r+20,y[n]+r,fill=f)
      self.C.create_text(x[n], y[n], text=gameslist[n][0], font=(None,12, 'bold'), width=85)

    #randomise games
    rand = list(range(len(gameslist)))
    random.shuffle(rand)
    #print(rand)
    #print(counter)

  #==================SPIN TO NEXT GAME====================#
  def spinGame(self):
    '''global gameslist'''
    global rand
    global counter
    global playerlist
    global promptlist
    global x
    global y
    global i
    global spinFlag

    if self.started == False:
      self.started = True
      self.spin_button.config(text='NEXT GAME')
      playsound(r'C:\Users\pbarr\Desktop\improv_dev\MonolougeBot-main\Air Horn.mp3',False)
      self.countdown()
    
    if counter >= len(gameslist):
      print('GAME FINISHED! RESET!')
      playsound(r'C:\Users\pbarr\Desktop\improv_dev\MonolougeBot-main\1up.mp3',False)
      self.score_label.configure(text='Games Played: '+str(counter))
      self.started = False
      self.spin_button['state'] = tkinter.DISABLED
      r=50
      prev_item = rand[counter-1]
      self.C.create_oval(x[prev_item]-r-20,y[prev_item]-r,x[prev_item]+r+20,y[prev_item]+r,fill='red')
      self.C.create_text(x[prev_item], y[prev_item], text=gameslist[prev_item][0], font=(None,12, 'bold'), width=80)
      self.reset_button.configure(bg='green')
      #self.title_label.config(text='C.A.R.L OFFLINE',fg='red')
    else:
      if counter > 0:
        playsound(r'C:\Users\pbarr\Desktop\improv_dev\MonolougeBot-main\1up.mp3',False)
      
      self.score_label.configure(text='Games Played: '+str(counter))
      r=55
      spin_counter = rand[counter]
      prev_item = rand[counter-1]
      if spinFlag == False:
        spinFlag = True
      else:
        self.C.create_oval(x[prev_item]-r-20,y[prev_item]-r,x[prev_item]+r+20,y[prev_item]+r,fill='red')
        self.C.create_text(x[prev_item], y[prev_item], text=gameslist[prev_item][0], font=(None,12, 'bold'), width=80)
      #print(spin_counter)
      spinbubble = self.C.create_oval(x[spin_counter]-r-20,y[spin_counter]-r,x[spin_counter]+r+20,y[spin_counter]+r,fill='green2')
      spintext = self.C.create_text(x[spin_counter], y[spin_counter], text=gameslist[spin_counter][0], font=(None,12, 'bold'), width=80)
      #print('Spinner Primed')
      #Update labels
      next_game = gameslist[rand[counter]][0]
      self.game_label.configure(text=next_game)
      print(next_game)
      
      num_of_players = gameslist[rand[counter]][1]+gameslist[rand[counter]][2]
      next_players = playerlist
      if counter == 0:
        random.shuffle(next_players)
        i = 0
      j = i + num_of_players
      #print ('j = ' + str(j))
      #print (len(next_players))
      if num_of_players == 0:
          self.players_label.configure(text='ALL PLAY')
      elif j == len(next_players):
          random.shuffle(next_players)
          i = 0
          j = i + num_of_players
          self.players_label.configure(text=f"HOST: {next_players[i]}\n{','.join(next_players[i+1:j])}")
      elif j > len(next_players):
          #print('Exceeded')
          i = j - num_of_players
          players_remaining = next_players[i:len(next_players)]
          players_needed = num_of_players - len(players_remaining)
          #print('Players needed: '+str(players_needed))
          while players_needed > 0:
              players_remaining.append('WILDCARD')
              players_needed -= 1
          #print(players_remaining)
          self.players_label.configure(text=f"HOST: {players_remaining[0]}\n{','.join(players_remaining[1:])}")
          random.shuffle(next_players)
          i = 0
      else:
          #print(next_players[0:num_of_players])
          self.players_label.configure(text=f"HOST: {next_players[i]}\n{','.join(next_players[i+1:j])}")
          #print(next_players)
          #print(next_players[i:j])
          i = j
            
      rand_promptlist = promptlist
      random.shuffle(rand_promptlist)
      if gameslist[rand[counter]][0]=='Genres' or gameslist[rand[counter]][0]=='Double Reverse Alphabet' or gameslist[rand[counter]][0]=='Pillars':
        #print('Special')
        print(gameslist[rand[counter]][3])
        rand_prompt = rand_promptlist[counter]
        next_prompt = gameslist[rand[counter]][3]
        #print(rand_prompt)
        self.prompts_label.configure(text=next_prompt+'\n'+'\n'+rand_prompt)
      elif gameslist[rand[counter]][3]=='':
        #print('Blank')
        rand_prompt = rand_promptlist[counter]
        print(rand_prompt)
        self.prompts_label.configure(text=rand_prompt)
      else:
        #print('Text')
        next_prompt = gameslist[rand[counter]][3]
        self.prompts_label.configure(text=next_prompt)
      counter += 1
      #print(num_of_players)
    

  #=======================GAME RESETTER===================#
  def resetGame(self):
    global counter
    global spinFlag
    global mm_left
    global ss_left
    self.start_button['state'] = tkinter.NORMAL
    self.reset_button['state'] = tkinter.DISABLED
    self.spin_button['state'] = tkinter.DISABLED
    self.game_label.configure(text='Game to be played')
    self.players_label.configure(text='Players Chosen')
    self.prompts_label.configure(text='Prompts')
    self.reset_button.configure(bg='SystemButtonFace')
    self.spin_button.config(text='START GAME')
    self.score_label.configure(text='Games Played: 0')
    spinFlag = False

    self.started = False
    mm_left = mm_default
    ss_left = ss_default
    time_left = str(mm_left).rjust(2,'0')+':'+str(ss_left).rjust(2,'0')
    self.timer_label.config(text=time_left,fg='black',font=(None,40,'bold'))
    
    counter = 0
    self.C.delete('all')
    #self.title_label.config(text='C.A.R.L OFFLINE',fg='red')
    print('Game RESET!')


  #=======================RESETTER CONFIRM================#
  def resetConfirm(self):
    answer = askyesno(title='Hello Dave', message='Are you sure you want to reset?')
    if answer:
      self.resetGame()


  def start(self):
    self.win.mainloop()

        




class Bubble(object):
  #Game bubbles to draw from list.
  def __init__(self, GameSpace, x, y, r, colour='Cyan', highlight=False):
    self.GameSpace = GameSpace
    self.x, self.y, self.r = x, y, r
    self.colour = colour
    
      
  




gamespace = GameSpace()
gamespace.win.title('C.A.R.L.')

gamespace.start()
