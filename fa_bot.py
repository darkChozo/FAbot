#!/usr/local/bin/python

import discord
import threading
import logging
import datetime
import pytz
import ConfigParser
import valve.source.a2s
import re
import string
import json

utc = pytz.utc

################################################################################
#   Server wrapper classes                                                     #
################################################################################


class GameServer(object):
    server = None

    def __init__(self, ip, port):
        self.server = valve.source.a2s.ServerQuerier((ip, port))

    def players(self):
        return self.server.get_players()

    def info(self):
        return self.server.get_info()

    def rules(self):
        return self.server.get_rules()

    def ping(self):
        return self.server.ping()

    def raw_info(self):
        self.server.request(valve.source.a2s.messages.InfoRequest())
        raw_msg = self.server.get_response()
        return filter(lambda x: x in string.printable, raw_msg)


class ArmaServer(GameServer):
    gamestate = {
        -1: "No Answer",
        1: "Server Empty / Mission Screen",
        3: "Lobby Waiting",
        5: "Loading Mission",
        6: "Briefing Screen",
        7: "In Progress",
        9: "Debriefing Screen",
        12: "Setting up",
        13: "Briefing",
        14: "Playing"
    }

    def __init__(self, ip, port):
        super(ArmaServer, self).__init__(ip, port)

    def state(self):
        # python-valve doesn't support the extended data field in the info
        # request message yet, so we have to do this by hand.
        # raw message looks like this:
        # IFolk ARPSAltisArma3fa3_a60_gamey_mission_v7@dw1.52.132676
        # bf,r152,n0,s1,i1,mf,lf,vt,dt,ttdm,g65545,hd12ce14a,c4194303-4194303,f0,pw,e0,j0,k0,

        self.server.request(valve.source.a2s.messages.InfoRequest())
        raw_msg = self.server.get_response()
        msg = filter(lambda x: x in string.printable, raw_msg)

        regex = re.compile(".*,s(?P<serverstate>\d*),.*,t(?P<gametype>\w*),.*")

        m = regex.search(msg, re.DOTALL)
        s = int(m.group('serverstate'))
        return [m.group('gametype'), self.gamestate[s]]


class InsurgencyServer(GameServer):
    def __init__(self, ip, port):
        super(InsurgencyServer, self).__init__(ip, port)

    def state(self):
        # python-valve doesn't support the extended data field in the info
        # request message yet, so we have to do this by hand.
        # raw message looks like this:
        # IFolk ARPSembassy_coopinsurgencyInsurgencydw2.0.4.2i~@checkpoint,theater:default,ver:2042,nwibanlist,nospawnprotection,f

        self.server.request(valve.source.a2s.messages.InfoRequest())
        raw_msg = self.server.get_response()
        msg = filter(lambda x: x in string.printable, raw_msg)

        regex = re.compile(".*,s(?P<serverstate>\d*),.*,t(?P<gametype>\w*),.*")

        m = regex.search(msg, re.DOTALL)
        s = int(m.group('serverstate'))
        return [m.group('gametype'), self.gamestate[s]]


################################################################################
#   Event Manager                                                              #
################################################################################
class EventManager(object):
    def __init__(self, channels):
        self.events = (
            ("The Folk ARPS Sunday Session", 6, 19, 20),
            ("The Folk ARPS Tuesday Session", 1, 19, 20)
        )
        self.warnings = (
            (" starts in five hours!", datetime.timedelta(hours=5)),
            (" starts in two hours!", datetime.timedelta(hours=2)),
            (" starts in thirty minutes!", datetime.timedelta(minutes=30)),
            (" is starting!", datetime.timedelta(0))
        )
        self.timezone = pytz.timezone("Europe/London")
        self.nextEvent = None
        self.timer = None
        self.channels = channels

    def handle_message(self, cli):
        if self.timer is None:
            self.find_next_event()
            if self.nextEvent is not None:
                for warning in self.warnings:
                    if self.nextEvent[1] - warning[1] > utc.localize(datetime.datetime.utcnow()):
                        seconds = (
                            self.nextEvent[1] - warning[1] - utc.localize(datetime.datetime.utcnow())).total_seconds()
                        self.timer = threading.Timer(seconds, self.handle_timer,
                                                     args=[cli, "@everyone " + self.nextEvent[0] + warning[0]])
                        self.timer.start()
                        print "created " + str(seconds) + "s timer for " + str(self.nextEvent)
                        break

    def handle_timer(self, cli, message):
        print "timer complete, printing """ + message + '"'
        self.timer = None
        for channel in self.channels:
            cli.send_message(client.get_channel(channel), message)

    def find_next_event(self):
        self.nextEvent = None
        now = utc.localize(datetime.datetime.utcnow())
        for event in self.events:
            t = self.timezone.localize(
                datetime.datetime.combine(self.next_weekday(event[1]), datetime.time(event[2], event[3])))
            t = t.astimezone(utc)
            if t > now and (self.nextEvent is None or t < self.nextEvent[1]):
                self.nextEvent = (event[0], t)

    def next_weekday(self, weekday):
        d = datetime.datetime.now(self.timezone).date()
        days_ahead = weekday - d.weekday()
        return d + datetime.timedelta(days_ahead)

################################################################################
#   FA Bot command functions logic                                             #
################################################################################

commands = {}


def command(cmd):
    """
    When you write a new command, add this decorator to it, so it's gets registered
    :param cmd:
    :return:
    """
    def wrapper(wrapped):
        commands[cmd] = wrapped

        return wrapped

    return wrapper


@command('help')
def help_cmd(message, args):
    """!help : display this text"""
    if not args:  # We don't want to spam chat because someone wanted to sing The Beatles in Spanish, do we?
        help_texts = ["Available commands:"]
        for item in commands.values():
            if item.func_doc:
                help_texts.append(item.func_doc)
        msg = '\n'.join(help_texts)
        client.send_message(message.channel, msg)


################################################################################
#   FA Bot command functions                                                   #
################################################################################


@command('status')
def status(message, args):
    """!status : reports the current state of the game on the Arma 3 server"""
    gametype, gamestate = arma_server.state()
    client.send_message(message.channel, gamestate)


@command('nextevent')
def nextevent(message, args):
    """!nextevent : reports the next scheduled Folk ARPS session"""
    client.send_message(
        message.channel,
        "Next event is {} at {}".format(manager.nextEvent[0], str(manager.nextEvent[1]))
    )


@command('armaserver')
def armaserver(message, args):
    """!armaserver : report the hostname and port of the Folk ARPS Arma server"""
    client.send_message(message.channel, "server.folkarps.com:2702")


@command('testserver')
def testserver(message, args):
    """!testserver : report the hostname and port of the Folk ARPS mission testing Arma server"""
    client.send_message(message.channel, "server.folkarps.com:2722")


@command('tsserver')
def tsserver(message, args):
    """!tsserver : report the hostname and port of the Folk ARPS teamspeak server"""
    client.send_message(message.channel, "server.folkarps.com:9988")


@command('github')
def github(message, args):
    """!github : report the URL of the FA_bot github project"""
    client.send_message(message.channel, "https://github.com/darkChozo/folkbot")


@command('ping')
def ping(message, args):
    """!ping : report the ping time from FA_bot to the Arma server"""
    ping = arma_server.ping()
    client.send_message(message.channel, "{} milliseconds".format(str(ping)))


@command('info')
def info(message, args):
    """!info : report some basic information on the Arma server"""
    info = arma_server.info()
    msg = "Arma 3 v{version} - {server_name} - {game} - {player_count}/{max_players} humans, {bot_count} AI on {map}"
    client.send_message(message.channel, msg.format(**info))


@command('players')
def players(message, args):
    """!players (insurgency) : show a list of players on the Arma (Insurgency) server"""
    if args == "insurgency":
        players = insurgency_server.players()
    else:
        players = arma_server.players()
    player_string = "Total players: {player_count}\n".format(**players)
    for player in sorted(players["players"], key=lambda p: p["score"], reverse=True):
        player_string += "{score} {name} (on for {duration} seconds)\n".format(**player)
    client.send_message(message.channel, player_string)


@command('rules')
def rules(message, args):
    """!rules : report on the cvars in force on the insurgency server"""
    # rules doesn't work for the arma server for some reason
    rules = insurgency_server.rules()
    client.send_message(message.channel, rules["rule_count"] + " rules")
    for rule in rules["rules"]:
        client.send_message(message.channel, rule)


@command('insurgency')
def insurgency(message, args):
    """!insurgency : report on the current state of the Folk ARPS Insurgency server"""
    msg = "Insurgency v{version} - {server_name} - {game} - {player_count}/{max_players} humans, {bot_count} AI on {map}"
    info = insurgency_server.info()
    client.send_message(message.channel, msg.format(**info))


@command('f3')
def f3(message, args):
    """!f3 : report the URL for the latest F3 release"""
    client.send_message( message.channel, "Latest F3 downloads: http://ferstaberinde.com/f3/en//index.php?title=Downloads")


@command('biki')
def biki(message, args):
    """!biki <term> : search the bohemia interactive wiki for <term>"""
    if args is not None:
        client.send_message(message.channel, "https://community.bistudio.com/wiki?search={}&title=Special%3ASearch&go=Go".format("+".join(args.split())))


@command('f3wiki')
def f3wiki(message, args):
    """!f3wiki <term> : search the f3 wiki for <term>"""
    if args is not None:
        client.send_message(message.channel, "http://ferstaberinde.com/f3/en//index.php?search={}&title=Special%3ASearch&go=Go".format("+".join(args.split())))


@command('test')
def test(message, args):
    # """!test : under development"""
    msg = arma_server.raw_info() + '\n\n' + insurgency_server.raw_info()
    client.send_message(message.channel, msg)


################################################################################
#   FA Bot                                                                     #
################################################################################
if __name__ == "__main__":
    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(filename="FA_bot.log", level=logging.DEBUG, format=FORMAT)
    logging.info("FAbot starting up")

    commandregex = re.compile("(?s)^!(?P<command>\w+)\s*(?P<args>.*)?")

    logging.info("Reading configuration")
    config = ConfigParser.RawConfigParser()
    config.read("config.ini")

    client_email = config.get("Config", "email")
    client_pass = config.get("Config", "password")

    manager_channels = json.loads(config.get("Config", "announcement_channels"))
    channel_whitelist = json.loads(config.get("Config", "channel_whitelist"))

    manager = EventManager(manager_channels)

    arma_server = ArmaServer(config.get("Config", "arma_server_ip"), int(config.get("Config", "arma_server_port")))
    insurgency_server = InsurgencyServer(config.get("Config", "insurgency_server_ip"), int(config.get("Config", "insurgency_server_port")))

    client = discord.Client()
    logging.info("Logging into Discord")
    client.login(client_email, client_pass)

    if not client.is_logged_in:
        logging.critical("Logging into Discord failed")
        print('Logging in to Discord failed')
        exit(1)

    @client.event
    def on_ready():
        print('Connected!')
        print('Username: ' + client.user.name)
        print('ID: ' + client.user.id)
        logging.info("Connected to Discord as %s (ID: %s)", client.user.name, client.user.id)

    @client.event
    def on_message(message):
        if (message.content[0]=="!"):
            if len(channel_whitelist) > 0 and message.channel.id not in channel_whitelist:
                return

            logging.info("#%s (%s) : %s",message.channel.name,message.author.name,message.content)

            manager.handle_message(client)

            cmdline = commandregex.search(message.content.lower())

            logging.debug("Command : %s(%s)",cmdline.group('command'),cmdline.group('args'))

            commands[cmdline.group('command')](message, cmdline.group('args'))


    logging.info("Entering main message event loop")
    client.run()
