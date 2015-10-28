# FAbot

discord.py-based bot for the Folk ARPS Discord server.

Currently allows for the following commands:

- !help
    Gives a list of commands.
- !github
    Gives the github URL for the bot
- !armaserver
- !testserver
- !tsserver
    Gives the hostname and port number for the main ARMA server, test ARMA
    server and Teamspeak server.
- !nextevent
    Lists the next scheduled Folk ARPS session
- !status
    Reports the game status on the main Folk ARPS ARMA server
- !ping
    Reports the ping time to the main Folk ARPS ARMA server
- !info
    Reports information on the main Folk ARPS ARMA server including map name,
    player count, game state and game type
- !players
    Reports the player count on the main server and a list of the players
- !insurgency
    Reports information on the Folk ARPS Insurgency server
- !biki *pagename*
    Searches the Bohemia Interactive Wiki 

# Configuration
Copy file config.ini.sample and rename duplicate to config.ini
Inside config file, fill out email and password, and if you want to test on your own server, change channels.

# Installation
If you're using virtualenv (you should) create it in subfolder .venv (it's gitignored).
To install (should take care of dependencies):
    python setup.py develop

# Development
To add new commands, you'll need to edit two places: "class Commands" and "def on_message"

Commands is a helper class, that keeps all available commands. Why is that important? Because it helps you not to worry about !help command!
Just add new command to it with code like
    foo = Command('!foo', '!foo *bar*')
First parameter is command user has to type, and second one (optional) will show up instead of the command when !help is printed.

on_message is the place where you'll be adding new stuff.
