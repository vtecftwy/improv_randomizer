import json
import logging
from pathlib import Path
from RandomChris.utils import get_config, get_paths, logthis

class ConfigManager:
    """Handles all configuration data management for the application.
    
    This class manages:
    - Master lists of cast, games, and prompts
    - Session-specific selections
    - Loading and saving of configuration data
    """
    
    def __init__(self):
        self.config = get_config()
        self.p2games, self.p2cast, self.p2prompts = get_paths()
        self.load_all_configs()
        
    def load_all_configs(self):
        """Load all configuration data from files"""
        logthis("Loading all configuration data")
        self.master_cast = self._load_master_cast()
        self.master_games = self._load_master_games()
        self.master_prompts = self._load_master_prompts()
        
        # Initialize session selections with all items selected by default
        self.session_cast = self.master_cast.copy()
        self.session_games = self.master_games.copy()
    
    def save_all_configs(self):
        """Save all configuration data to files"""
        logthis("Saving all configuration data")
        self._save_master_cast()
        self._save_master_games()
        self._save_master_prompts()
        self._save_session_cast()
        self._save_session_games()
    
    def _load_master_cast(self):
        """Load master cast list from file"""
        with open(self.p2cast, 'r') as fp:
            return [line.strip() for line in fp.readlines()]
    
    def _save_master_cast(self):
        """Save master cast list to file"""
        with open(self.p2cast, 'w') as fp:
            fp.write('\n'.join(self.master_cast))
    
    def _load_master_games(self):
        """Load master games list from file"""
        with open(self.p2games, 'r') as fp:
            return json.load(fp)
    
    def _save_master_games(self):
        """Save master games list to file"""
        with open(self.p2games, 'w') as fp:
            json.dump(self.master_games, fp, indent=4)
    
    def _load_master_prompts(self):
        """Load master prompts list from file"""
        with open(self.p2prompts, 'r') as fp:
            return [line.strip() for line in fp.readlines()]
    
    def _save_master_prompts(self):
        """Save master prompts list to file"""
        with open(self.p2prompts, 'w') as fp:
            fp.write('\n'.join(self.master_prompts))
    
    def _save_session_cast(self):
        """Save session cast selection to file"""
        session_cast_file = self.p2cast.parent / f"session-{self.p2cast.name}"
        with open(session_cast_file, 'w') as fp:
            fp.write('\n'.join(self.session_cast))
    
    def _save_session_games(self):
        """Save session games selection to file"""
        session_games_file = self.p2games.parent / f"session-{self.p2games.name}"
        with open(session_games_file, 'w') as fp:
            json.dump(self.session_games, fp, indent=4)
    
    def add_cast_member(self, name):
        """Add a new cast member to the master list"""
        if name not in self.master_cast:
            self.master_cast.append(name)
            self._save_master_cast()
    
    def remove_cast_member(self, name):
        """Remove a cast member from the master list"""
        if name in self.master_cast:
            self.master_cast.remove(name)
            if name in self.session_cast:
                self.session_cast.remove(name)
            self._save_master_cast()
            self._save_session_cast()
    
    def add_game(self, game_data):
        """Add a new game to the master list"""
        game_id = str(len(self.master_games) + 1)
        self.master_games[game_id] = game_data
        self._save_master_games()
    
    def remove_game(self, game_id):
        """Remove a game from the master list"""
        if game_id in self.master_games:
            del self.master_games[game_id]
            if game_id in self.session_games:
                del self.session_games[game_id]
            self._save_master_games()
            self._save_session_games()
    
    def add_prompt(self, prompt):
        """Add a new prompt to the master list"""
        if prompt not in self.master_prompts:
            self.master_prompts.append(prompt)
            self._save_master_prompts()
    
    def remove_prompt(self, prompt):
        """Remove a prompt from the master list"""
        if prompt in self.master_prompts:
            self.master_prompts.remove(prompt)
            self._save_master_prompts()
    
    def update_session_cast(self, selected_cast):
        """Update the session cast selection"""
        self.session_cast = selected_cast
        self._save_session_cast()
    
    def update_session_games(self, selected_games):
        """Update the session games selection"""
        self.session_games = selected_games
        self._save_session_games() 