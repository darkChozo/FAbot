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
To add new commands, you'll need to write a new function to do the actual
command, taking two arguments:
- *message* The actual discord message object which contains things like the
    channel, the author, the content and so on; and
- *args* Any arguments that follow the actual command itself (so in _"!foo bar"_,
    args would be 'bar'

Your function must test for the case where *message* is _None_, and return a
text string if it is; this is usage message, which gets reported by the FAbot
_!help_ command. 

Once your function is written, you must edit the *commands* dict and add an
entry linking the command name you want to use with your new function:

``` 
commands = {'usage'      : help,
            'help'       : help}
```

So here the user can use either _"!usage"_ or _"!help"_ and in both cases the
help() function will be called. 
