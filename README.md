# improv_randomizer
A simple tool for randomized short games for improv.

You can customize the following by updating a few files:
- the cast members (text tile)
- the games to play and their characteristics (jsom file)
- a list of prompts to use randomly for game which do not explicitely require a specific prompt (text file)
- the background image (in config file)
- the duration of a session (in config file)
- custom configurations for speficic session (in a subfolder, defined in the config file)

For each game, a host and players are randomly drawn from the cast, in a way that keeps cummulative participation by each cast member as player and host more of less equal.
  
For each game, it is possible to exclude one or several cast members as player or host. It is also possible to retrict hosting to a specific list of cast member.
