import tkinter as tk
from tkinter import ttk, messagebox
from RandomChris.config_manager import ConfigManager
from RandomChris.utils import logthis

class ConfigWindow:
    """Configuration window for managing cast, games, and prompts."""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Configuration")
        self.window.geometry("800x600")
        
        self.config_manager = ConfigManager()
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.cast_tab = ttk.Frame(self.notebook)
        self.games_tab = ttk.Frame(self.notebook)
        self.prompts_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.cast_tab, text="Cast")
        self.notebook.add(self.games_tab, text="Games")
        self.notebook.add(self.prompts_tab, text="Prompts")
        
        # Initialize each tab's content
        self._init_cast_tab()
        self._init_games_tab()
        self._init_prompts_tab()
        
        # Add save button at the bottom
        self.save_btn = ttk.Button(
            self.window, text="Save All Changes",
            command=self._save_changes
        )
        self.save_btn.pack(pady=10)
    
    def _init_cast_tab(self):
        # Split into two frames
        master_frame = ttk.LabelFrame(self.cast_tab, text="Master Cast List")
        master_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        session_frame = ttk.LabelFrame(self.cast_tab, text="Session Cast")
        session_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Master cast list with add/remove/edit functionality
        self.master_cast_list = tk.Listbox(master_frame)
        self.master_cast_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Buttons for master cast management
        btn_frame = ttk.Frame(master_frame)
        ttk.Button(btn_frame, text="Add", command=self._add_cast).pack(pady=2)
        ttk.Button(btn_frame, text="Remove", command=self._remove_cast).pack(pady=2)
        ttk.Button(btn_frame, text="Edit", command=self._edit_cast).pack(pady=2)
        btn_frame.pack(side=tk.RIGHT)
        
        # Session cast selection with checkboxes
        self.session_cast_frame = ttk.Frame(session_frame)
        self.session_cast_frame.pack(fill=tk.BOTH, expand=True)
        self.session_cast_vars = {}  # Dictionary to store checkbox variables
        self._refresh_session_cast()
    
    def _init_games_tab(self):
        # Split into two frames
        master_frame = ttk.LabelFrame(self.games_tab, text="Master Games List")
        master_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        session_frame = ttk.LabelFrame(self.games_tab, text="Session Games")
        session_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Master games list with add/remove/edit functionality
        self.master_games_tree = ttk.Treeview(
            master_frame,
            columns=("name", "players", "audience", "category"),
            show="headings"
        )
        self.master_games_tree.heading("name", text="Name")
        self.master_games_tree.heading("players", text="Players")
        self.master_games_tree.heading("audience", text="Audience")
        self.master_games_tree.heading("category", text="Category")
        self.master_games_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Buttons for master games management
        btn_frame = ttk.Frame(master_frame)
        ttk.Button(btn_frame, text="Add", command=self._add_game).pack(pady=2)
        ttk.Button(btn_frame, text="Remove", command=self._remove_game).pack(pady=2)
        ttk.Button(btn_frame, text="Edit", command=self._edit_game).pack(pady=2)
        ttk.Button(btn_frame, text="Rules", command=self._edit_game_rules).pack(pady=2)
        btn_frame.pack(side=tk.RIGHT)
        
        # Session games selection with checkboxes
        self.session_games_frame = ttk.Frame(session_frame)
        self.session_games_frame.pack(fill=tk.BOTH, expand=True)
        self.session_games_vars = {}  # Dictionary to store checkbox variables
        self._refresh_session_games()
    
    def _init_prompts_tab(self):
        # Prompts list with add/remove/edit functionality
        self.prompts_list = tk.Listbox(self.prompts_tab)
        self.prompts_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Buttons for prompts management
        btn_frame = ttk.Frame(self.prompts_tab)
        ttk.Button(btn_frame, text="Add", command=self._add_prompt).pack(pady=2)
        ttk.Button(btn_frame, text="Remove", command=self._remove_prompt).pack(pady=2)
        ttk.Button(btn_frame, text="Edit", command=self._edit_prompt).pack(pady=2)
        btn_frame.pack(side=tk.RIGHT)
        
        self._refresh_prompts()
    
    def _refresh_session_cast(self):
        # Clear existing widgets
        for widget in self.session_cast_frame.winfo_children():
            widget.destroy()
        self.session_cast_vars.clear()
        
        # Create checkboxes for each cast member
        for i, name in enumerate(self.config_manager.master_cast):
            var = tk.BooleanVar(value=name in self.config_manager.session_cast)
            self.session_cast_vars[name] = var
            ttk.Checkbutton(
                self.session_cast_frame,
                text=name,
                variable=var
            ).grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)
    
    def _refresh_session_games(self):
        # Clear existing widgets
        for widget in self.session_games_frame.winfo_children():
            widget.destroy()
        self.session_games_vars.clear()
        
        # Create checkboxes for each game
        for i, (game_id, game) in enumerate(self.config_manager.master_games.items()):
            var = tk.BooleanVar(value=game_id in self.config_manager.session_games)
            self.session_games_vars[game_id] = var
            ttk.Checkbutton(
                self.session_games_frame,
                text=game['name'],
                variable=var
            ).grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)
    
    def _refresh_prompts(self):
        self.prompts_list.delete(0, tk.END)
        for prompt in self.config_manager.master_prompts:
            self.prompts_list.insert(tk.END, prompt)
    
    def _add_cast(self):
        name = self._get_input("Add Cast Member", "Enter name:")
        if name:
            self.config_manager.add_cast_member(name)
            self._refresh_session_cast()
    
    def _remove_cast(self):
        selection = self.master_cast_list.curselection()
        if selection:
            name = self.master_cast_list.get(selection[0])
            if messagebox.askyesno("Confirm", f"Remove {name} from cast?"):
                self.config_manager.remove_cast_member(name)
                self._refresh_session_cast()
    
    def _edit_cast(self):
        selection = self.master_cast_list.curselection()
        if selection:
            old_name = self.master_cast_list.get(selection[0])
            new_name = self._get_input("Edit Cast Member", "Enter new name:", old_name)
            if new_name:
                self.config_manager.remove_cast_member(old_name)
                self.config_manager.add_cast_member(new_name)
                self._refresh_session_cast()
    
    def _add_game(self):
        # Create a dialog for game details
        dialog = GameDialog(self.window, "Add Game")
        if dialog.result:
            self.config_manager.add_game(dialog.result)
            self._refresh_session_games()
    
    def _remove_game(self):
        selection = self.master_games_tree.selection()
        if selection:
            game_id = selection[0]
            if messagebox.askyesno("Confirm", "Remove selected game?"):
                self.config_manager.remove_game(game_id)
                self._refresh_session_games()
    
    def _edit_game(self):
        selection = self.master_games_tree.selection()
        if selection:
            game_id = selection[0]
            game_data = self.config_manager.master_games[game_id]
            dialog = GameDialog(self.window, "Edit Game", game_data)
            if dialog.result:
                self.config_manager.master_games[game_id] = dialog.result
                self._refresh_session_games()
    
    def _edit_game_rules(self):
        selection = self.master_games_tree.selection()
        if selection:
            game_id = selection[0]
            game_data = self.config_manager.master_games[game_id]
            dialog = GameRulesDialog(self.window, game_data, self.config_manager.master_cast)
            if dialog.result:
                self.config_manager.master_games[game_id].update(dialog.result)
                self._refresh_session_games()
    
    def _add_prompt(self):
        prompt = self._get_input("Add Prompt", "Enter prompt:")
        if prompt:
            self.config_manager.add_prompt(prompt)
            self._refresh_prompts()
    
    def _remove_prompt(self):
        selection = self.prompts_list.curselection()
        if selection:
            prompt = self.prompts_list.get(selection[0])
            if messagebox.askyesno("Confirm", "Remove selected prompt?"):
                self.config_manager.remove_prompt(prompt)
                self._refresh_prompts()
    
    def _edit_prompt(self):
        selection = self.prompts_list.curselection()
        if selection:
            old_prompt = self.prompts_list.get(selection[0])
            new_prompt = self._get_input("Edit Prompt", "Enter new prompt:", old_prompt)
            if new_prompt:
                self.config_manager.remove_prompt(old_prompt)
                self.config_manager.add_prompt(new_prompt)
                self._refresh_prompts()
    
    def _get_input(self, title, prompt, default=""):
        """Show a dialog to get user input"""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text=prompt).pack(pady=5)
        entry = ttk.Entry(dialog, width=40)
        entry.insert(0, default)
        entry.pack(pady=5)
        
        result = [None]  # Use list to store result
        
        def on_ok():
            result[0] = entry.get()
            dialog.destroy()
        
        ttk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
        
        dialog.transient(self.window)
        dialog.grab_set()
        self.window.wait_window(dialog)
        return result[0]
    
    def _save_changes(self):
        # Update session selections
        selected_cast = [
            name for name, var in self.session_cast_vars.items()
            if var.get()
        ]
        self.config_manager.update_session_cast(selected_cast)
        
        selected_games = {
            game_id for game_id, var in self.session_games_vars.items()
            if var.get()
        }
        self.config_manager.update_session_games(selected_games)
        
        # Save all changes
        self.config_manager.save_all_configs()
        messagebox.showinfo("Success", "All changes saved successfully")
        self.window.destroy()


class GameDialog:
    """Dialog for adding/editing game details"""
    
    def __init__(self, parent, title, game_data=None):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x300")
        
        self.result = None
        
        # Create form fields
        ttk.Label(self.window, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.window, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.window, text="Number of Players:").grid(row=1, column=0, padx=5, pady=5)
        self.players_entry = ttk.Entry(self.window, width=10)
        self.players_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.window, text="Number of Audience:").grid(row=2, column=0, padx=5, pady=5)
        self.audience_entry = ttk.Entry(self.window, width=10)
        self.audience_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.window, text="Category:").grid(row=3, column=0, padx=5, pady=5)
        self.category_entry = ttk.Entry(self.window, width=40)
        self.category_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(self.window, text="Prompt:").grid(row=4, column=0, padx=5, pady=5)
        self.prompt_text = tk.Text(self.window, width=40, height=5)
        self.prompt_text.grid(row=4, column=1, padx=5, pady=5)
        
        # Fill in existing data if editing
        if game_data:
            self.name_entry.insert(0, game_data.get('name', ''))
            self.players_entry.insert(0, str(game_data.get('nbr_players', 0)))
            self.audience_entry.insert(0, str(game_data.get('nbr_audience', 0)))
            self.category_entry.insert(0, game_data.get('category', ''))
            self.prompt_text.insert('1.0', game_data.get('prompt', ''))
        
        # Add buttons
        btn_frame = ttk.Frame(self.window)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="OK", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        self.window.transient(parent)
        self.window.grab_set()
        parent.wait_window(self.window)
    
    def _on_ok(self):
        try:
            self.result = {
                'name': self.name_entry.get(),
                'nbr_players': int(self.players_entry.get()),
                'nbr_audience': int(self.audience_entry.get()),
                'category': self.category_entry.get(),
                'prompt': self.prompt_text.get('1.0', 'end-1c'),
                'exclude': [],
                'host_include': [],
                'host_exclude': []
            }
            self.window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for players and audience")


class GameRulesDialog:
    """Dialog for editing game rules (exclude, host_include, host_exclude)"""
    
    def __init__(self, parent, game_data, cast_list):
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Game Rules")
        self.window.geometry("600x400")
        
        self.result = None
        
        # Create three frames for each rule type
        exclude_frame = ttk.LabelFrame(self.window, text="Exclude from Game")
        exclude_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        host_include_frame = ttk.LabelFrame(self.window, text="Include as Host")
        host_include_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        host_exclude_frame = ttk.LabelFrame(self.window, text="Exclude as Host")
        host_exclude_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create checkboxes for each cast member in each frame
        self.exclude_vars = {}
        self.host_include_vars = {}
        self.host_exclude_vars = {}
        
        for i, name in enumerate(cast_list):
            # Exclude checkboxes
            var = tk.BooleanVar(value=name in game_data.get('exclude', []))
            self.exclude_vars[name] = var
            ttk.Checkbutton(
                exclude_frame,
                text=name,
                variable=var
            ).grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)
            
            # Host include checkboxes
            var = tk.BooleanVar(value=name in game_data.get('host_include', []))
            self.host_include_vars[name] = var
            ttk.Checkbutton(
                host_include_frame,
                text=name,
                variable=var
            ).grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)
            
            # Host exclude checkboxes
            var = tk.BooleanVar(value=name in game_data.get('host_exclude', []))
            self.host_exclude_vars[name] = var
            ttk.Checkbutton(
                host_exclude_frame,
                text=name,
                variable=var
            ).grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)
        
        # Add buttons
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="OK", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        self.window.transient(parent)
        self.window.grab_set()
        parent.wait_window(self.window)
    
    def _on_ok(self):
        self.result = {
            'exclude': [
                name for name, var in self.exclude_vars.items()
                if var.get()
            ],
            'host_include': [
                name for name, var in self.host_include_vars.items()
                if var.get()
            ],
            'host_exclude': [
                name for name, var in self.host_exclude_vars.items()
                if var.get()
            ]
        }
        self.window.destroy() 