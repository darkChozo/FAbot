#!/usr/local/bin/python
import logging
import re
import discord_client
import config_manager
import event_manager
import game_server
import watcher
import requests
import json
import subprocess


def command(cmd):
    """When you write a new command, add this decorator to it, so it gets registered"""
    def outerwrap(function):
        def innerwrap(*args):
            args[0].commands[cmd] = function
            function(*args)
        return innerwrap
    return outerwrap


class FAbot(object):
    def __init__(self, configfilename):
        self.client_email = None
        self.client_pass = None
        self.discordClient = None
        self.event_manager = None
        self.main_watcher = None
        self.game_servers = {}
        self.commandregex = re.compile("(?s)^!(?P<command>\w+)\s*(?P<args>.*)?")
        self.commands = {}
        self.botMethods = ['start', 'stop']
        self.FAMDB_API_key = None
        self.FAMDB_app_id = None

        # Logging
        logging.basicConfig(filename="log/FA_bot.log", level=logging.DEBUG,
                            format="%(asctime)-15s %(message)s")
        logging.info("FAbot starting up")
        logging.info("Registering commands: ")
        for method in dir(self):
            if callable(getattr(self, method)):
                if method[:2] != '__' and method not in self.botMethods:
                    call = getattr(self, method)
                    call(None, None)
                    logging.info(method)

        logging.info("Full command list:")
        logging.info(self.commands)

        # Configuration file
        logging.info("Reading configuration")
        self.config = config_manager.ConfigManager(configfilename)

    def start(self):
        self.event_manager = event_manager.EventManager()
        self.main_watcher = watcher.Watcher(self)

        self.event_manager.announcement_channels = self.config.get_json("announcement_channels", default=[])

        # TODO: probably event manager should take channels from client instead?

        # Game servers
        self.game_servers['arma'] = game_server.ArmaServer(
            ip=self.config.get("arma_server_ip"),
            port=int(self.config.get("arma_server_port"))
        )
        self.game_servers['insurgency'] = game_server.InsurgencyServer(
            ip=self.config.get("insurgency_server_ip"),
            port=int(self.config.get("insurgency_server_port"))
        )

        # FAMDB
        self.FAMDB_API_key = self.config.get("API_key", section="FAMDB")
        self.FAMDB_app_id  = self.config.get("application_id", section="FAMDB")

        # Discord client
        logging.info("Logging into Discord")
        self.discordClient = discord_client.Client(self)

        self.discordClient.channel_whitelist = self.config.get_json("channel_whitelist", default=[])
        self.discordClient.announcement_channels = self.config.get_json("announcement_channels", default=[])

        self.discordClient.welcome_pm = self.config.get("welcome_pm", section="Announcements")
        self.discordClient.join_announcement = self.config.get("join_announcement", section="Announcements")
        self.discordClient.leave_announcement = self.config.get("leave_announcement", section="Announcements")

        self.client_email = self.config.get("email", section="Bot Account")
        self.client_pass = self.config.get("password", section="Bot Account")

        if self.client_email is None or self.client_pass is None:
            logging.critical("Could not find Discord authentication details "
                             "in config file.")
            print("Could not find Discord authentication details.")
            exit(1)

        self.discordClient.login(self.client_email, self.client_pass)

        if not self.discordClient.is_logged_in:
            logging.critical("Logging into Discord failed")
            print('Logging in to Discord failed')
            exit(1)

        logging.info("Starting main watcher")
        self.main_watcher.start()

        logging.info("Entering main message event loop")
        self.discordClient.run()

    def stop(self):
        self.discordClient.logout()
        if self.event_manager.timer is not None:  # Todo: move that one to event manager? Maybe not needed.
            self.event_manager.timer.cancel()
        self.main_watcher.stop()

    @command('help')
    def help_cmd(self, message, args):
        """!help : display this text"""
        # We don't want to spam chat because someone wanted
        # to sing The Beatles in Spanish, do we?
        if not args:
            help_texts = ["Available commands:"]
            for item in self.commands.values():
                if item.func_doc:
                    help_texts.append(item.func_doc)
            msg = '\n'.join(help_texts)
            return msg

    @command('github')
    def github(self, message, args):
        """!github : report the URL of the FA_bot github project"""
        if message is None:
            return None
        return "https://github.com/darkChozo/folkbot"

    @command('status')
    def status(self, message, args):
        """!status : reports the current state of the game on the Arma server"""
        if message is None:
            return None
        gametype, gamestate = self.game_servers['arma'].state()
        return gamestate

    @command('nextevent')
    def nextevent(self, message, args):
        """!nextevent : reports the next scheduled Folk ARPS session"""
        if message is None:
            return None
        return self.event_manager.next_event_message()

    @command('armaserver')
    def armaserver(self, message, args):
        """!armaserver : report the hostname and port of the Folk ARPS Arma server"""
        if message is None:
            return None
        return "server.folkarps.com:2702"

    @command('testserver')
    def testserver(self, message, args):
        """!testserver : report the hostname and port of the Folk ARPS mission testing Arma server"""
        if message is None:
            return None
        return "server.folkarps.com:2722"

    @command('tsserver')
    def tsserver(self, message, args):
        """!tsserver : report the hostname and port of the Folk ARPS teamspeak server"""
        if message is None:
            return None
        return "server.folkarps.com:9988"

    @command('ping')
    def ping(self, message, args):
        """!ping : report the ping time from FA_bot to the Arma server"""
        if message is None:
            return None
        ping = self.game_servers['arma'].ping()
        return "{} milliseconds".format(str(ping))

    @command('info')
    def info(self, message, args):
        """!info : report some basic information on the Arma server"""
        if message is None:
            return None
        info = self.game_servers['arma'].info()
        msg = "Arma 3 v{version} - {server_name} - {game} - {player_count}/{max_players} humans, {bot_count} AI on {map}"
        return msg.format(**info)

    @command('players')
    def players(self, message, args):
        """!players (insurgency) : show a list of players on the Arma (Insurgency) server"""
        if message is None:
            return None
        if args == "insurgency":
            players = self.game_servers['insurgency'].players()
        else:
            players = self.game_servers['arma'].players()
        player_string = "Total players: {player_count}\n".format(**players)
        for player in sorted(players["players"],
                             key=lambda p: p["score"],
                             reverse=True):
            player_string += "{score} {name} (on for {duration} seconds)\n".format(**player)
        return player_string

    @command('rules')
    def rules(self, message, args):
        """!rules : report on the cvars in force on the insurgency server"""
        if message is None:
            return None
        # rules doesn't work for the arma server for some reason
        rules = self.game_servers['insurgency'].rules()
        msg = rules["rule_count"] + " rules:\n"
        msg += "\n".join(rules["rules"])
        return msg

    @command('insurgency')
    def insurgency(self, message, args):
        """!insurgency : report on the current state of the Folk ARPS Insurgency server"""
        if message is None:
            return None
        msg = "Insurgency v{version} - {server_name} - {game} - {player_count}/{max_players} humans, {bot_count} AI on {map}"
        info = self.game_servers['insurgency'].info()
        return msg.format(**info)

    @command('f3')
    def f3(self, message, args):
        """!f3 : report the URL for the latest F3 release"""
        if message is None:
            return None
        return "Latest F3 downloads: http://ferstaberinde.com/f3/en//index.php?title=Downloads"

    @command('biki')
    def biki(self, message, args):
        """!biki <term> : search the bohemia interactive wiki for <term>"""
        if message is None:
            return None
        if args is not None:
            return "https://community.bistudio.com/wiki?search={}&title=Special%3ASearch&go=Go".format("+".join(args.split()))

    @command('f3wiki')
    def f3wiki(self, message, args):
        """!f3wiki <term> : search the f3 wiki for <term>"""
        if message is None:
            return None
        if args is not None:
            return "http://ferstaberinde.com/f3/en//index.php?search={}&title=Special%3ASearch&go=Go".format("+".join(args.split()))

    @command('session')
    def session(self, message, args):
        """!session  : show whether or not a Folk ARPS session is running
        !session start : tell the bot a Folk ARPS session is starting
        !session stop : tell the bot a Folk ARPS session is ending"""
        if message is None:
            return None
        if args == "start":
            self.main_watcher.start()
        elif args == "stop":
            self.main_watcher.stop()
        else:
            if self.main_watcher.session.isSet():
                return "Folk ARPS session underway; FA_bot will announce when we're slotting"
            else:
                return "No Folk ARPS session running at the moment. Check when the next event is on with !nextevent"

    @command('addons')
    def addons(self, message, args):
        """!addons : display link to FA optional addons"""
        return "http://www.folkarps.com/forum/viewtopic.php?f=43&t=1382"

    @command('test')
    def test(self, message, args):
        # """!test : under development"""
        if message is None:
            return None
        logging.info('test()')
        msg = self.game_servers['arma'].raw_info() + '\n\n' + self.game_servers['insurgency'].raw_info()
        return msg

    @command('mission')
    def mission(self, message, args):
        # """!mission <missionname> : describe <missionname> or the mission currently being played on the server"""
        if message is None:
            return None
        logging.info('mission(%(args)s)' % {'args': args})

        if (args is None) or (not args.strip()):
            logging.info('No mission name specified, interrogating arma server')
            servermapname = self.game_servers['arma'].info()['game']
            regex = re.compile("fa3_[c|a]\w.[0-9]*_(?P<mapname>\w+)[_v[0-9]*]?")
            logging.info('Server map name: %s' % servermapname)
            result = regex.search(servermapname)
            if result.groups is None:
                logging.info("Didn't recognise the server map name")
                return "Need a mission name (didn't recognise the one on the server right now)"
            tokenlist = result.group('mapname').split('_')
            args = max(tokenlist, key=len)
            logging.info('Map name tokens : %s',tokenlist)
            logging.info('Selected search token : %s',args)

        if (args is None) or (not args):
            logging.info("Didn't recognise the server map name")
            return "Need a mission name (didn't recognise the one on the server right now)"

        header = {'X-Parse-Application-Id' : self.FAMDB_app_id,
                  'X-Parse-REST-API-Key'   : self.FAMDB_API_key,
                  'Content-Type'           : 'application/json'}

        query = {'where': json.dumps({'missionName' : { '$regex' : '\Q%s\E' % args, '$options' : 'i'}})}
        logging.info('Query: %s' % query)

        response = requests.get('https://api.parse.com/1/classes/Missions', headers=header, params=query)
        logging.info('URL: %s' % response.url)

        result = response.json()
        bestguess = result['results'][0]
        logging.info('Response: %s ' % bestguess)

        data = {'servername': servermapname,
                'name': bestguess[u'missionName'],
                'type': bestguess[u'missionType'],
                'map':bestguess[u'missionMap'],
                'author':bestguess[u'missionAuthor'],
                'description':bestguess[u'missionDesc']}

        if not servermapname:
            msg = "**Mission name: {name}**\n"
        else:
            msg = "**Mission name: {name}** *({servername})*\n"

        msg = ' '.join( ( msg, "**Mission type:** {type}\n" \
                        "**Location:** {map}\n" \
                        "**Author:** {author}\n" \
                        "**Description:** {description}\n" ) )

        logging.info(msg.format(**data))
        return msg.format(**data)

    @command('update')
    def update(self, message, args):
        # """!update : tell the bot to get its latest release from github and restart. Permission required."""
        if message is None:
            return None

        try:
            git_result = subprocess.check_output('git pull', shell=True)
            logging.info(git_result)
            if (git_result == 'Already up-to-date.'):
                return git_result

            msg = ' '.join(("**Restarting for update:**\n```", git_result, "```"))
            self.discordClient.announce(msg)
            open('update','w').close()
            self.stop()

        except subprocess.CalledProcessError as err:
            logging.info(err)
            logging.info(' '.join(('shell: ', err.cmd)))
            logging.info(' '.join(('output:', err.output)))
            msg = ' '.join(('**Update failed:** ',str(err)))
            return msg
