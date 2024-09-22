import datetime as dt
import json
import numpy as np
import random

from pathlib import Path
from utils import *

config_dict = get_config()
GAME_DURATION = dt.timedelta(minutes=config_dict['duration-minutes'], seconds=0)

p2games, p2cast, p2prompts = get_paths()

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
        self.last_five_minutes_starded = False

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
        
        self.game_categories = sorted(list(set([g.category for g in self.games])))
        self.played_categories_counts = {cat: 0 for cat in self.game_categories}

        # Handle prompts
        with open(p2prompts, 'r') as fp:
            lines = fp.readlines()
        self.promptlist = [line.removesuffix('\n').strip() for line in lines]

        logthis('   Game session data loaded')
        print(f"{len(self.cast)} cast members: {', '.join(player_names)}\n")
        print(f"{self.nbr_games} games")
        for g in self.gamedict.values():
            print(f" - {g['name']}")

    @monitor_fn
    def create_game_sequence(self):
        """Create a random sequence of games, by defining a sequence of game indices"""
        # purely random sequence of games
        # self.game_sequence = list(range(self.nbr_games))
        # random.shuffle(self.game_sequence)
        
        # pick game sequence randomly with the following constraints:
        #  - no two games from the same category follow each other
        #  - no game is played twice in the same session
        #  - all categories are represented in a quasi-equal number of games
        self.shuffled_categories = random.sample(self.game_categories, len(self.game_categories))
        games_per_category = {cat: [g for g in self.games if g.category == cat] for cat in self.shuffled_categories}
        for cat in self.shuffled_categories:
            games_per_category[cat] = random.sample(games_per_category[cat], len(games_per_category[cat]))
        
        games_randomized = []
        while any([len(games_per_category[cat]) > 0 for cat in self.shuffled_categories]):
            for cat in self.shuffled_categories:
                if len(games_per_category[cat]) > 0:
                    game = games_per_category[cat].pop()
                    games_randomized.append(game)            
        
        self.game_sequence = [self.games.index(g) for g in games_randomized]
        # print(self.game_sequence)
        # print('\n'.join([f"{g.name:30s} {g.category}" for g in games_randomized]))
                            

    @monitor_fn
    def show_cast(self):
        """Print all info on cast"""
        for player in self.cast:
            print(player)

    @staticmethod
    def compute_probs(counts, cast_masks, method='linear', factor=25, l=0.5):
        """Compute probabilities for picking cast member based on counts and cast_mask

        Probabilities are computed using a linear or exponential function of the counts, and then
        are normalized using a softmax for those indexes not masked by cast_mask.
        """

        if method == 'linear':
            weights = factor/(counts + 1)
        elif method == 'exponential':
            lambda_ = l
            weights = np.exp(-lambda_ * counts)
        else:
            raise AttributeError(f'Unknown method {method}, should be `linear` or `exponential`')

        # Calculate softmax of weights, using only indices where cast_mask==True, all others = 0
        selected_idx = np.arange(len(weights))[cast_masks]
        softmax = np.zeros_like(weights)
        softmax[selected_idx] = np.exp(weights[selected_idx]) / np.sum(np.exp(weights[selected_idx]), axis=0)

        return softmax

    @monitor_fn
    def pick_cast(self, game):
        """Pick host and players for the game

        Randomly select a host and players for the game, based on:
        - the host_exclude and host_include lists for the game
        - the player exlude list for the game
        - the nbr_games_hosted attribute of each cast member (how many games already hosted so far)
        - the nbr_games_played attribute of each cast member (how many games already hosted so far)

        Returns:
            idxs_host:    index of host in `self.cast`
            host_name:    name of host
            idxs_players: list of indexes in `self.cast` for picked players
            player_names: list of names of picked players
        """

        cast_names = np.array([player.name for player in self.cast])
        logthis(f"   Cast Names: {cast_names}")

        # Pick one host for the game
        # 1. Pick possible hosts based on host_include and host_exclude lists
        if game.host_include:
            possible_hosts = game.host_include
            logthis(f"   Possible hosts: {possible_hosts}. From host_include list")
        else:
            possible_hosts = [player.name for player in self.cast if player.name not in game.host_exclude]
            logthis(f"   Possible hosts: {possible_hosts}. From cast minus host_exclude")
        # 2. Calculate a hosting probability distribution for each cast member
        cast_hosting_counts = np.array([player.nbr_games_hosted for player in self.cast])
        cast_mask = [name in possible_hosts for name in cast_names] # True if cast member is a possible host
        probs_hosting = self.compute_probs(counts=cast_hosting_counts, cast_masks=cast_mask)
        logthis(f"   Cast Hosting Counts: {cast_hosting_counts}")
        logthis(f"   Cast Mask: {cast_mask}")
        logthis(f"   Probs Hosting: {probs_hosting}")
        # 3. Draw one cast member from the discrete probability distribution
        host_idx = np.sort(np.random.choice(np.arange(self.nbr_players), size=1, p=probs_hosting, replace=False))[0]
        host_name = cast_names[host_idx]
        logthis(f"   Host Index: {host_idx} Host Name: {host_name}")

        # 4. Increment the nbr_games_hosted attribute of the host
        self.cast[host_idx].nbr_games_hosted += 1

        # Pick players for the game
        # 1. Pick possible players based on player exclude list
        cast_game_counts = np.array([player.nbr_games_played for player in self.cast])
        cast_mask = [game.name not in player.game_exclusion_list for player in self.cast]
        cast_mask[host_idx] = False

        #  2. Calculate a playing probability distribution for each cast member
        probs_playing = self.compute_probs(cast_game_counts, cast_mask) 
        logthis(f"   Cast Game Counts: {cast_game_counts}")
        logthis(f"   Cast Mask: {cast_mask}. From cast minus host and game_exclusion_list")
        logthis(f"   Probs Playing: {probs_playing}")

        # 3. Draw a sample of players from the discrete probability distribution
        nbr_players = game.nbr_players if game.nbr_players > 0 else sum(cast_mask) # nbr_players is 0 if the game is for the whole cast
        players_idxs = np.sort(np.random.choice(np.arange(self.nbr_players), size=nbr_players, p=probs_playing, replace=False))
        logthis(f"   Players Indexes: {players_idxs}")

        # 4. Increment nbr_games_played for the picked players
        for player_idx in players_idxs:
            self.cast[player_idx].nbr_games_played += 1

        return host_idx, host_name, players_idxs.tolist(), cast_names[players_idxs].tolist()     

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


class Game:
    """Object including all information and methods related to a game"""

    def __init__(self, gameinfo:dict) -> None:
        logthis(f'   Creating new Game object for {gameinfo["name"]}')
        required_keys = ['name', 'nbr_players', 'nbr_audience']
        optional_keys = ['prompt', 'include', 'exclude', 'description', 'tips']

        for k, v in gameinfo.items():
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
        self.nbr_games_hosted = 0

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


if __name__ == '__main__':
    pass
    print(f"{'='*15} Running GameSession test {'='*15}\n")  
    # setup_logging()
    
    session = GameSession()
    print([session.games[idx].name for idx in session.game_sequence], '\n')
    for i in range(1,11):
        session.create_game_sequence()
        print(f"Game Sequence {i}:")
        print('\n'.join([f"   - {session.games[idx].category:20s}: {session.games[idx].name}" for idx in session.game_sequence]))

    print('Done')