import datetime as dt
import json
import numpy as np
import random

from pathlib import Path
from utils import *

GAME_DURATION = dt.timedelta(minutes=45, seconds=0)


ROOT = Path(__file__).resolve().parent
p2games = ROOT/ 'games.json'
p2cast = ROOT/ 'cast.txt'
p2prompts = ROOT/ 'prompts.txt'

assert p2games.exists(), f'File {p2games} does not exist'
assert p2cast.exists(), f'File {p2cast} does not exist'
assert p2prompts.exists(), f'File {p2prompts} does not exist'

class GameSession:
    """Handles the logic of the game session

    - Loading the games, cast, prompts information from respective files
    - Logic to randomly pick next games and cast members
    - Store the state of the game session, including start time, current game, cast' cummulated played games
    - Handle transitions between games

    This class does not handle any GUI aspects of the game. It is only a data structure and a logic engine.
    """

    @monitor_fn
    def __init__(self) -> None:
        logthis(f"  Creating new GameSession object")
        self.load_session_info()
        self.create_game_sequence()
        self.session_started = False
        self.session_finished = False
        self.start_time = None
        self.step = None
        self.nbr_games_played = None
        self.current_game_idx = None
        self.previous_game_idx = None

        logthis(f"   step: {self.step}, games played: {self.nbr_games_played}, curr: {self.current_game_idx}, prev: {self.previous_game_idx}")

    @monitor_fn
    def load_session_info(self, shuffle=False):
        """Load games, cast and prompt info from files"""
        # Load games
        with open(p2games, 'r') as fp:
            game_json = json.load(fp)
        # convert string keys into int keys
        self.gamedict = {int(i):d for i, d in game_json.items()}
        # create a list of Game objects, one object per game in the list
        self.games = [Game(d) for d in self.gamedict.values()]
        # when option is True, shuffle the list of games to randomize the order (default is False)
        if shuffle:
            random.shuffle(self.games)
        self.nbr_games = len(self.games)

        # Handle cast
        with open(p2cast, 'r') as fp:
            lines = fp.readlines()
        player_names = [line.removesuffix('\n').strip() for line in lines]
        self.cast = [Player(name, games=self.games) for name in player_names]
        self.nbr_players = len(self.cast)

        # Handle prompts
        with open(p2prompts, 'r') as fp:
            lines = fp.readlines()
        self.promptlist = [line.removesuffix('\n').strip() for line in lines]

        logthis('   Game session data loaded')

    @monitor_fn
    def create_game_sequence(self):
        """Create a random sequence of games, by defining a sequence of game indices"""
        self.game_sequence = list(range(self.nbr_games))
        random.shuffle(self.game_sequence)

    @monitor_fn
    def show_cast(self):
        """Print all info on cast"""
        for player in self.cast:
            print(player)

    @monitor_fn
    def pick_players(self, game, method='linear', factor=25, l=0.5):
        """Pick players for the game

        The method ramdomly picks players from the cast for the given game.
        Picking gives priority to players who played less games so far in this session.
        It also excludes players listed in the exclusion list for the game.

        Returns: 
            idxs_picked:  list of indexes in `session.cast` for picked players
            player_names: list of names of picked players
        """
        player_names = np.array([player.name for player in self.cast])
        # player_joining_game is a boolean list, True if player can join the game, False if it is excluded
        player_joining_game = [game.name not in player.game_exclusion_list for player in self.cast]
        player_game_count = np.array([player.nbr_games_played for player in self.cast])
        
        if method == 'linear':
            weights = factor/(player_game_count+1)
        elif method == 'exponential':
            lambda_ = l
            weights = np.exp(-lambda_ * player_game_count)
        else:
            raise AttributeError(f'Unknown method {method}, should be `linear` or `exponential`')
        
        probabilities = self.masked_softmax(weights, mask=player_joining_game)
        
        # Draw a sample from the discrete probability distribution
        nbr_players = game.nbr_players if game.nbr_players > 0 else sum(player_joining_game) # nbr_players is 0 if the game is for the whole cast
        idxs_picked = np.sort(np.random.choice(np.arange(self.nbr_players), size=nbr_players, p=probabilities, replace=False))

        return idxs_picked.tolist(), player_names[idxs_picked].tolist()

    @monitor_fn
    def pick_next_game(self):
        """Pick the next game to play"""
        logthis(f"   curr: {self.current_game_idx}, prev: {self.previous_game_idx}, games left  {len(self.game_sequence)}")
        # If first game in the session, one time intialization:
        if not self.session_started:
            self.session_started = True
            self.start_time = dt.datetime.now()

        # As long as there are possible games to play:
        if self.game_sequence:
            logthis(f"   Picking next game from {len(self.game_sequence)} games.")
            self.step = self.step + 1 if self.step is not None else 1
            self.nbr_games_played = self.nbr_games_played + 1 if self.nbr_games_played is not None else 0
            self.previous_game_idx = self.current_game_idx
            self.current_game_idx = self.game_sequence.pop()
        # When there are no more games to play:
        else:
            logthis(f"   No more games to play, {self.game_sequence}")
            self.nbr_games_played += 1
            self.previous_game_idx = self.current_game_idx
            self.current_game_idx = None
            self.session_finished = True
        logthis(f"   step: {self.step} nbr_games_played: {self.nbr_games_played} prev: {self.previous_game_idx}, curr: {self.current_game_idx}, finished: {self.session_finished}")


    @property
    def time_left(self) -> dt.timedelta:
        """Return the time left for the game, as a deltatime object"""
        left_time =  self.start_time + GAME_DURATION - dt.datetime.now()
        zero = dt.timedelta(seconds=0)
        return max(left_time, zero)
        
    @staticmethod
    def masked_softmax(x, mask):
        """Calculate softmax of x, using only indices where mask==True, all others = 0"""
        selected_idx = np.arange(len(x))[mask]
        softmax = np.zeros_like(x)
        softmax[selected_idx] = np.exp(x[selected_idx]) / np.sum(np.exp(x[selected_idx]), axis=0)
        return softmax

class Game:
    """Object including all information and methods related to a game"""

    def __init__(self, gameinfo:dict) -> None:
        logthis(f'   Creating new Game object for {gameinfo["name"]}')
        required_keys = ['name', 'nbr_players', 'nbr_audience']
        optional_keys = ['prompt', 'include', 'exclude', 'description', 'tips']

        for k, v in gameinfo.items():
            # self.__setattr__(k, v)
            setattr(self, k, v)
        for k in required_keys:
            assert k in gameinfo.keys(), f'Key {k} is missing from gameinfo dict'
        for k in optional_keys:
            if k not in gameinfo.keys():
                # self.__setattr__(k, None)
                setattr(self, k, None)

        self.host = None
        self.players = None
        self.status = 'unplayed' # unplayed, playing, played

    def info(self):
        """Return a list of attributes of the game"""
        return [k for k in self.__dict__.keys() if not k.startswith('__')]

    def __repr__(self) -> str:
        text = f"{self.__class__} at 0x{hex(id(self))}" + '\n'
        for attr in self.info():
            text = text + f"    {attr:15s}: {getattr(self, attr)}" + '\n'
        return text

    def __str__(self) -> str:
        text = 'Game Info: \n'
        for attr in self.info():
            text = text + f"    {attr:15s}: {getattr(self, attr)}" + '\n'
        return text
    
class Player:
    """Object including all information and methods related to a player"""

    def __init__(self, name, games) -> None:
        logthis(f"   Creating new Player object for {name}")
        self.name = name
        self.nbr_games_played = 0

        # create list of inclusion and exclusion for this player
        self.hosting_inclusion_list = [
            g.name for g in games if self.name in getattr(g, 'host_include', [])
            ]
        self.hosting_exclusion_list = [
            g.name for g in games 
            if self.name in getattr(g, 'host_exlude', []) 
            or ('All Others' in getattr(g, 'host_exclude') and not self.name in getattr(g, 'host_include', []))
            ]
        self.game_exclusion_list = [
            g.name for g in games if self.name in getattr(g, 'exclude', [])
            ]

    def info(self):
        """Return a list of attributes of the players"""
        return [k for k in self.__dict__.keys() if not k.startswith('__')]

    def __repr__(self) -> str:
        text = f"{self.__class__} at 0x{hex(id(self))}" + '\n'
        for attr in self.info():
            text = text + f"    {attr:15s}: {getattr(self, attr)}" + '\n'
        return text

    def __str__(self) -> str:
        text = 'Player Info: \n'
        for attr in self.info():
            text = text + f"    {attr:15s}: {getattr(self, attr)}" + '\n'
        return text

        