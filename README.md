# RandomChris
`RandomChris` runs **C.H.R.I.S.**, a tool that serves improv short games in a random order and with random players.

We forgot what **C.H.R.I.S.** stands for, but it must have been one of these:

- Could Hosts Randomly Inspire Scenes
- Could Humor Run Improvised Sets
- Chaos Happens Randomly In Scene
- Could Hilarity Reside in Surprises
- Chaotic Humor Random Improv Scene
- Comedy Hilarious Rehearsal Improvisation Shuffler
- Comedic Hosting and Randomization Integrated System
- Curated Hilarious Random Improv Setup
- Creative Hilarious Role Improv Sequencer
- Cast Hosting and Random Improv Selector
- Comic Hosts Random Improv Scene
- Comedy Hosts and Random Improv System
- Cleverly Hosted Randomized Improv System
- Comedian's Helper for Random Improv Selection
- Comedy-Hosted Randomized Improv Scheduler
- Could Humor Randomly Influence Scenes
- Comedic Hosting Randomization and Improv Selector 


**C.H.R.I.S** can be customized for the following aspects:
- The **names of cast members**, among which players will be drawn for each game.
- The **games**, among which the games to play will be picked, with their respective characteristics.
- The total **duration** of a game session.
- The background image for the screen.
- A list of **prompts** to use randomly for game which do not explicitely given a specific prompt.
- A set of constraints for the games

## How it works?:
- Each time the `Start`/`Next` button is clicked, a new game is randomly picked.

<img src="assets/img/screenshot-tool.png">

- For each game, the correct number of players is drawn from the cast, and one cast member is drawn as host. Players are randomly picked from the cast in a way that keeps cummulative participation by each member as player and as host more of less equal when many games are played.
- The game name, the selected players and the host are brought to the screen, as well as a prompt. When the game requires audience members to join on stage, their number will be indicated as well.
- A count down is started when the first game starts, from the defined total duration. When the counter reaches zero, the game session ends. 
- A sound is played at each game transition, when the session starts and when it ends.

## Customization:
- By default, the package will look for configuration information in file `config.cfg`, if it exists, and in file `config-default.cfg`  otherwise. The default configuration file comes with repo.
- The configuration file defines six parameters (see below for default values):
  - `duration-minutes = 45`
  - `cast = cast.txt`  (the text file name where the cast member names are stored)
  - `games = games.json` (the JSON file name where the games info are stored)
  - `prompts =  prompts.txt` (the text file name where the random prompts are stored)
  - `cfg-folder` =  (a folder under `config` where custom configuration files are stored, by default, files are directly under `config`)
  - `background-image` = bg_1100x700.png

- A jupyter notebook in the project root `cast-configuration-tool.ipynb` makes it easier to change cast member's names, update games and update prompts.

    <img src="assets/img/screenshot-config-cast.png">
    <img src="assets/img/screenshot-config-games.png">
    
- For each game, it is possible to exclude one or several cast members as player or host. When names are in the exclusion list for a specific game, their name will not be picked in the corresponding role. It is also possible to restrict hosting to a specific list of cast member, that is the host will only be picked in the list provoded for the game.

    <img src="assets/img/screenshot-config-games-cast.png">

- The `games.json` file has the following structure, with the same entries for each game. _Note that `"description"` and `"tips"` are currently not used_:
```json
{
    "1": {
        "name": "A Date with Me",
        "nbr_players": 0,
        "nbr_audience": 0,
        "prompt": "A date with me is like <object/occupation>.",
        "exclude": [],
        "host_include": [],
        "host_exclude": [],
        "description": null,
        "tips": null,
        "category": "All Play"
    },
    "2": {
        "name": "Double Reverse Alphabet",
        "nbr_players": 2,
        "nbr_audience": 0,
        "prompt": "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z What is a non romantic relationship.",
        "exclude": [],
        "host_include": [],
        "host_exclude": [],
        "description": null,
        "tips": null,
        "category": "Limitation"
    }
}
```
- It is possible to create a configuration using a `cfg-folder`, which means the package will use the cast, games and prompts file under that `cfg-folder` instead. This allows to create several custom configurations and switch from one to the other only by changing `config.cfg` or `config-default.cfg`. 
