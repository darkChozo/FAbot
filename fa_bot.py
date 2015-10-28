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


class EventManager(object):
    def __init__(self, channels, arma_server, insurgency_server):
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
        self.server = valve.source.a2s.ServerQuerier((arma_server['ip'], arma_server['port']))
        self.insurgencyServer = valve.source.a2s.ServerQuerier((insurgency_server['ip'], insurgency_server['port']))
        
        self.gamestate = {
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

    def players(self):
        players = self.server.get_players()
        return players

    def info(self):
        info = self.server.get_info()
        return info

    def rules(self):
        rules = self.server.get_rules()
        return rules

    def ping(self):
        ping = self.server.ping()
        return ping

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

    def in_info(self):
        info = self.insurgencyServer.get_info()
        return info

    def get_raw_in_info(self):
        self.insurgencyServer.request(valve.source.a2s.messages.InfoRequest())
        raw_msg = self.insurgencyServer.get_response()
        return filter(lambda x: x in string.printable, raw_msg)


class Commands(object):
    class Command(object):
        def __init__(self, command, help_text=None):
            self.command = command
            self.help_text = help_text

    armaserver = Command('!armaserver', '!armaserver')
    biki = Command('!biki', '!biki *pagename*')
    f3 = Command('!f3', '!f3')
    f3wiki = Command('!f3wiki', '!f3wiki *pagename*')
    github = Command('!github', '!github')
    help = Command('!help', '!help')
    info = Command('!info', '!info')
    insurgency = Command('!insurgency', '!insurgency')
    nextevent = Command('!nextevent', '!nextevent')
    ping = Command('!ping', '!ping')
    players = Command('!players', '!players')
    rules = Command('!rules', '!rules')
    status = Command('!status', '!status')
    test = Command('!test')
    testserver = Command('!testserver', '!testserver')
    tsserver = Command('!tsserver', '!tsserver')


if __name__ == "__main__":
    bikiregex = re.compile("^(?i)!biki ((\w)*)$")
    f3wikiregex = re.compile("^(?i)!f3wiki ((\w)*)$")

    logging.basicConfig()

    config = ConfigParser.RawConfigParser()
    config.read("config.ini")

    client_email = config.get("Config", "email")
    client_pass = config.get("Config", "password")

    manager_channels = json.loads(config.get("Config", "channel_whitelist"))
    manager_arma_server = {
        'ip': config.get("Config", "arma_server_ip"),
        'port': int(config.get("Config", "arma_server_port"))
    }
    manager_insurgency_server = {
        'ip': config.get("Config", "insurgency_server_ip"),
        'port': int(config.get("Config", "insurgency_server_port"))
    }
    manager = EventManager(manager_channels, manager_arma_server, manager_insurgency_server)

    client = discord.Client()
    client.login(client_email, client_pass)

    if not client.is_logged_in:
        print('Logging in to Discord failed')
        exit(1)


    @client.event
    def on_ready():
        print('Connected!')
        print('Username: ' + client.user.name)
        print('ID: ' + client.user.id)


    @client.event
    def on_message(message):
        if message.channel.id not in manager.channels:
            return

        manager.handle_message(client)
        content = message.content.lower()

        if content == Commands.status.command:
            gametype, gamestate = manager.state()
            client.send_message(message.channel, gamestate)

        elif content == Commands.help.command:
            help_texts = []
            for key, item in Commands.__dict__.items():
                if type(item).__name__ == 'Command':
                    if item.help_text is not None:
                        help_texts.append(item.help_text)
            msg = ', '.join(help_texts)
            client.send_message(message.channel, msg)

        elif content == Commands.nextevent.command:
            client.send_message(
                message.channel,
                "Next event is {} at {}".format(manager.nextEvent[0], str(manager.nextEvent[1]))
            )

        elif content == Commands.armaserver.command:
            client.send_message(message.channel, "server.folkarps.com:2702")

        elif content == Commands.testserver.command:
            client.send_message(message.channel, "server.folkarps.com:2722")

        elif content == Commands.tsserver.command:
            client.send_message(message.channel, "server.folkarps.com:9988")

        elif content == Commands.github.command:
            client.send_message(message.channel, "https://github.com/darkChozo/folkbot")

        elif content == Commands.ping.command:
            ping = manager.ping()
            client.send_message(message.channel, "{} milliseconds".format(str(ping)))

        elif content == Commands.info.command:
            info = manager.info()
            msg = "Arma 3 v{version} - {server_name} - {game} - {player_count}/{max_players} humans," \
                  " {bot_count} AI on {map}"
            client.send_message(message.channel, msg.format(**info))

        elif content == Commands.players.command:
            players = manager.players()
            player_string = "Total players: {player_count}\n".format(**players)
            for player in sorted(players["players"], key=lambda p: p["score"], reverse=True):
                player_string += "{score} {name} (on for {duration} seconds)\n".format(**player)
            client.send_message(message.channel, player_string)

        elif content == Commands.rules.command:
            rules = manager.rules()
            client.send_message(message.channel, rules["rule_count"] + " rules")
            for rule in rules["rules"]:
                client.send_message(message.channel, rule)

        elif content == Commands.insurgency.command:
            msg = "Insurgency v{version} - {server_name} - {game} - {player_count}/{max_players} humans," \
                  " {bot_count} AI on {map}"
            info = manager.in_info()
            client.send_message(message.channel, msg.format(**info))

        elif content == Commands.f3.command:
            client.send_message(
                message.channel,
                "Latest F3 downloads: http://ferstaberinde.com/f3/en//index.php?title=Downloads"
            )

        elif content.startswith(Commands.biki.command):
            bikimatch = bikiregex.match(message.content)
            if bikimatch is not None:
                client.send_message(
                    message.channel,
                    "https://community.bistudio.com/wiki?search={}&title=Special%3ASearch&go=Go".format(
                        bikimatch.group(1)
                    )
                )

        elif content.startswith(Commands.f3wiki.command):
            f3wikimatch = f3wikiregex.match(message.content)
            if f3wikimatch is not None:
                client.send_message(
                    message.channel,
                    "http://ferstaberinde.com/f3/en//index.php?search={}&title=Special%3ASearch&go=Go".format(
                        f3wikimatch.group(1)
                    )
                )

        elif content == Commands.test.command:
            msg = manager.get_raw_in_info()
            client.send_message(message.channel, msg)

    client.run()
