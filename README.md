# improv_randomizer
A simple tool for randomized short games for improv.

The following can be customized:
- **names of cast members**, among which players will be picked for each game.
- **games**, and their characteristics, among which games to play will be picked.
- list of **prompts** to use randomly for game which do not explicitely require a specific prompt
- the background image
- the **duration** of a session (in config file)

## How it works?:
- Each time the button is clicked, a new game is randomly picked among the possible ones
- For each game, a host and the correct number of players are randomly drawn from the cast. Players are drawned from the cast in a way that keeps cummulative participation by each cast member as player and host more of less equal.
- The game name, the selected players and host as well as a prompt will be brought to the screen
- A sound is played at each game transition
- A count down is started when the first game starts, from the defined total duration. When the counter reaches zero, the game session ends. 

## Customization:
- By default, the package will look a the file `config.cfg`, if it exists, otherwise in `config-default.cfg` with is in this repo. Therefore anyone can create one of several custom configurations. Configuration file defines four values (see below for default values)
  - `duration-minutes = 45`
  - `cast = cast.txt` provide the text file name where the cast member names are stored
  - `games = games.json` provide the JSON file name where the games info are stored
  - `prompts =  prompts.txt` provided the text file name where the radom prompts are stored 
- The jupyter notebook in the project root `cast-configuration-tool.ipynb` makes it easer to change cast member's names and update games.
- For each game, it is possible to exclude one or several cast members as player or host. It is also possible to retrict hosting to a specific list of cast member.
