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

logging.basicConfig()

config = ConfigParser.RawConfigParser()
config.read("config.ini")

client = discord.Client()
client.login(config.get("Config","email"),config.get("Config","password"))

if not client.is_logged_in:
    print('Logging in to Discord failed')
    exit(1)

utc = pytz.utc
bikiregex = re.compile("^(?i)!biki ((\w)*)$")
channelwhitelist = config.get("Config","channelwhitelist").replace(" ","").split(",")
if (channelwhitelist[0] == '') :
    channelwhitelist = []

class EventManager :
    events = (("The Folk ARPS Sunday Session", 6, 19, 20), ("The Folk ARPS Tuesday Session", 1, 19, 20))
    warnings = ((" starts in five hours!", datetime.timedelta(hours=5)),(" starts in two hours!", datetime.timedelta(hours=2)),(" starts in thirty minutes!",datetime.timedelta(minutes=30)),(" is starting!", datetime.timedelta(0)))
    timezone = pytz.timezone("Europe/London")
    nextEvent = None
    timer = None
    channels = ["107862710267453440"]
    server = valve.source.a2s.ServerQuerier(('91.121.223.212', 2703))
    insurgencyServer = valve.source.a2s.ServerQuerier(('91.121.223.212', 27015))

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

    def handleMessage(self, client) :
        if (self.timer is None) :
            self.findNextEvent()
            if (self.nextEvent is not None) :
                for warning in self.warnings :
                    if (self.nextEvent[1] - warning[1] > utc.localize(datetime.datetime.utcnow())) :
                        seconds = (self.nextEvent[1] - warning[1] - utc.localize(datetime.datetime.utcnow())).total_seconds()
                        self.timer = threading.Timer(seconds, self.handleTimer, args=[client, "@everyone " + self.nextEvent[0] + warning[0]])
                        self.timer.start()
                        print "created " + str(seconds) + "s timer for " + str(self.nextEvent)
                        break

    def handleTimer(self, client, message) :
        print "timer complete, printing """ + message + '"'
        self.timer = None
        for channel in self.channels :
            client.send_message(client.get_channel(channel), message)

    def findNextEvent(self) :
        self.nextEvent = None
        now = utc.localize(datetime.datetime.utcnow());
        for event in self.events :
            t = self.timezone.localize(datetime.datetime.combine(self.nextWeekday(event[1]), datetime.time(event[2], event[3])))
            t = t.astimezone(utc)
            if (t > now and (self.nextEvent is None or t < self.nextEvent[1])) :
                self.nextEvent = (event[0], t)

    def nextWeekday(self, weekday):
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
        rawMsg = self.server.get_response()
        msg = filter(lambda x: x in string.printable, rawMsg)

        regex = re.compile(".*,s(?P<serverstate>\d*),.*,t(?P<gametype>\w*),.*")

        m = regex.search(msg,re.DOTALL)
        s = int(m.group('serverstate'))
        return [m.group('gametype'), self.gamestate[s]]

    def in_info(self):
        info = self.insurgencyServer.get_info()
        return info

    def get_raw_in_info(self):
        self.insurgencyServer.request(valve.source.a2s.messages.InfoRequest())
        rawMsg = self.insurgencyServer.get_response()
        return filter(lambda x: x in string.printable, rawMsg)

manager = EventManager()

@client.event
def on_ready():
    print('Connected!')
    print('Username: ' + client.user.name)
    print('ID: ' + client.user.id)

@client.event
def on_message(message):
    if (len(channelwhitelist) != 0 and message.channel.id not in channelwhitelist) :
        return
    manager.handleMessage(client)
    content = message.content.lower()
    if (content == "!help") :
        client.send_message(message.channel, "Available commands: !armaserver, !testserver, !tsserver, !nextevent, !github, !status, !ping, !info, !players, !biki *pagename*, !insurgency")
    if (content == "!status") :
        gametype,gamestate = manager.state()
        client.send_message(message.channel, gamestate)
    if (content == "!nextevent") :
        client.send_message(message.channel, "Next event is " + manager.nextEvent[0] + " at " + str(manager.nextEvent[1]))
    if (content == "!armaserver") :
        client.send_message(message.channel, "server.folkarps.com:2702")
    if (content == "!testserver") :
        client.send_message(message.channel, "server.folkarps.com:2722")
    if (content == "!tsserver") :
        client.send_message(message.channel, "server.folkarps.com:9988")
    if (content == "!github") :
        client.send_message(message.channel, "https://github.com/darkChozo/folkbot")
    if (content == "!ping") :
        ping = manager.ping()
        client.send_message(message.channel, str(ping) + " milliseconds")
    if (content == "!info") :
        info = manager.info()
        gametype,gamestate = manager.state()
        client.send_message(message.channel, "Arma 3 v{version} - {server_name} - {game} (".format(**info) + gametype + ") - {player_count}/{max_players} humans, {bot_count} AI on {map} - ".format(**info) + gamestate)
    if (content == "!players") :
        players = manager.players()
        playerString = "Total players: {player_count}\n".format(**players)
        for player in sorted(players["players"], key=lambda p: p["score"], reverse=True):
            playerString += "{score} {name} (on for {duration} seconds)\n".format(**player)
        client.send_message(message.channel, playerString)
    if (content == "!insurgency") :
        info = manager.in_info()
        client.send_message(message.channel, "Insurgency v{version} - {server_name} - {game} - {player_count}/{max_players} humans, {bot_count} AI on {map}".format(**info))
    if (content == "!test") :
        msg = manager.get_raw_in_info()
        client.send_message(message.channel, msg)

    bikimatch = bikiregex.match(message.content)
    if (bikimatch is not None) :
        client.send_message(message.channel, "https://community.bistudio.com/wiki?search="  + bikimatch.group(1) + "&title=Special%3ASearch&go=Go")


client.run()
