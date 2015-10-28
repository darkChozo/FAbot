#!/usr/local/bin/python

import discord
import threading
import logging
import datetime
import pytz
import ConfigParser
import valve.source.a2s
import re

logging.basicConfig()

config = ConfigParser.RawConfigParser()
config.read("config.ini")

client = discord.Client()
client.login(config.get("Config", "email"), config.get("Config", "password"))

if not client.is_logged_in:
    print('Logging in to Discord failed')
    exit(1)

utc = pytz.utc
bikiregex = re.compile("^(?i)!biki ((\w)*)$")
f3wikiregex = re.compile("^(?i)!f3wiki ((\w)*)$")


class EventManager(object):
    events = (("The Folk ARPS Sunday Session", 6, 19, 20), ("The Folk ARPS Tuesday Session", 1, 19, 20))
    warnings = (
        (" starts in five hours!", datetime.timedelta(hours=5)), (" starts in two hours!", datetime.timedelta(hours=2)),
        (" starts in thirty minutes!", datetime.timedelta(minutes=30)), (" is starting!", datetime.timedelta(0)))
    timezone = pytz.timezone("Europe/London")
    nextEvent = None
    timer = None
    # channels = ["107862710267453440"]
    channels = ["103777679739748352"]
    server = valve.source.a2s.ServerQuerier(('91.121.223.212', 2703))
    insurgencyServer = valve.source.a2s.ServerQuerier(('91.121.223.212', 27015))

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

    def in_info(self):
        info = self.insurgencyServer.get_info()
        return info


manager = EventManager()


@client.event
def on_ready():
    print('Connected!')
    print('Username: ' + client.user.name)
    print('ID: ' + client.user.id)


@client.event
def on_message(message):
    manager.handle_message(client)
    content = message.content.lower()

    bikimatch = bikiregex.match(message.content)
    f3wikimatch = f3wikiregex.match(message.content)

    if content == "!status":
        client.send_message(message.channel, "Working. Probably.")
    elif content == "!nextevent":
        client.send_message(message.channel,
                            "Next event is " + manager.nextEvent[0] + " at " + str(manager.nextEvent[1]))
    elif content == "!armaserver":
        client.send_message(message.channel, "server.folkarps.com:2702")
    elif content == "!testserver":
        client.send_message(message.channel, "server.folkarps.com:2722")
    elif content == "!tsserver":
        client.send_message(message.channel, "server.folkarps.com:9988")
    elif content == "!github":
        client.send_message(message.channel, "https://github.com/darkChozo/folkbot")
    elif content == "!ping":
        ping = manager.ping()
        client.send_message(message.channel, str(ping) + " milliseconds")
    elif content == "!info":
        info = manager.info()
        msg = "Arma 3 v{version} - {server_name} - {game} - {player_count}/{max_players} humans," \
              " {bot_count} AI on {map}"
        client.send_message(message.channel, msg.format(**info))
    elif content == "!players":
        players = manager.players()
        player_string = "Total players: {player_count}\n".format(**players)
        for player in sorted(players["players"], key=lambda p: p["score"], reverse=True):
            player_string += "{score} {name} (on for {duration} seconds)\n".format(**player)
        client.send_message(message.channel, player_string)
    elif content == "!rules":
        rules = manager.rules()
        client.send_message(message.channel, rules["rule_count"] + " rules")
        for rule in rules["rules"]:
            client.send_message(message.channel, rule)
    elif content == "!insurgency":
        msg = "Insurgency v{version} - {server_name} - {game} - {player_count}/{max_players} humans," \
              " {bot_count} AI on {map}"
        info = manager.in_info()
        client.send_message(message.channel, msg.format(**info))
    elif content == "!f3":
        client.send_message(
            message.channel,
            "Latest F3 downloads: http://ferstaberinde.com/f3/en//index.php?title=Downloads"
        )
    elif bikimatch is not None:
        client.send_message(message.channel, "https://community.bistudio.com/wiki?search=" + bikimatch.group(
            1) + "&title=Special%3ASearch&go=Go")
    elif f3wikimatch is not None:
        client.send_message(message.channel, "http://ferstaberinde.com/f3/en//index.php?search=" + f3wikimatch.group(
            1) + "&title=Special%3ASearch&go=Go")
    elif content == "!help":
        msg = "Available commands: !armaserver, !testserver, !tsserver, !nextevent, !github," \
              " !status, !ping, !info, !players, !biki *pagename*"
        client.send_message(message.channel, msg)


client.run()
