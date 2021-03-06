FAbot
=====

discord.py-based bot created for the Folk ARPS Discord server.
Bot is configurable, so it can be used with other communities.

### Features
FAbot Currently allows for the following commands:
* !help - Gives a list of commands.
* !github - Gives the github URL for the bot
* !armaserver - Gives the address of the main Arma Server
* !testserver - Gives the address of the test / mission maker Arma Server
* !tsserver - Gives the hostname and port number for the main ARMA server, test ARMA server and Teamspeak server
* !nextevent - Lists the next scheduled Folk ARPS session
* !status - Reports the game status on the main Folk ARPS ARMA server
* !ping - Reports the ping time to the main Folk ARPS ARMA server
* !info - Reports information on the main Folk ARPS ARMA server including map name, player count, game state and game type
* !players - Reports the player count on the main server and a list of the players
* !insurgency - Reports information on the Folk ARPS Insurgency server
* !f3 - Gives the address to latest f3 framework download
* !f3wiki *pagename* - Searches the f3 Wiki
* !biki *pagename* - Searches the Bohemia Interactive Wiki
* !mission *missionname* - Searches FAMDB for the mission name and reports some of its details; if no mission name is specified, it tries to search for the mission currently running on the server (but this may fail)

# Installation
If you're using virtualenv (you should) create it in subfolder .venv (it's gitignored).
To install (it should take care of dependencies):
```
python setup.py develop
```

If running as a daemon, this can be run using the daemontools supervisor;
create a symbolic link for the installation directory in /service (or use
update-service --add *dirname* on Debian)

# Configuration
Copy file config.ini.sample and rename duplicate to config.ini
Inside config file, fill out email and password, and if you want to test on your own server, change channels.

### Custom messages
Section "Announcements" in config let's you enable and customize "user join server" and "user left server" messages.
You can also enable PM sent to every new user.

# Development
To add new commands, you'll need to write a new method in FAbot.py to do the actual command, taking three arguments:
- *self*
- *message* The actual discord message object which contains things like the
    channel, the author, the content and so on; and
- *args* Any arguments that follow the actual command itself (so in _"!foo bar"_,
    args would be 'bar'

Your function must return String, that will be sent as a response, or return nothing.

You *must* test *message* at the very start of your method and return None
immediately if *message* is None.

If you want your function to show up once someone writes _!help_,
in the first line of the function write documentation for it. Documentation is just a line of text
starting and ending with *"""*. Keep it formatted like documentation of other functions.

Once your function is written, you must add @command decorator to it.
Just write @decorator('command') before it's declared.

Example of new method:

```
@command("foo")
def bar(self, message, args):
    """!foo : display bar"""
    if message is None:
        return None

    return "bar"
```
