import discord;
import threading;
import logging;
import datetime;
import pytz;
import ConfigParser

logging.basicConfig()

config = ConfigParser.RawConfigParser()
config.read("config.ini")

client = discord.Client();
client.login(config.get("Config","email"),config.get("Config","password"));

if not client.is_logged_in:
    print('Logging in to Discord failed')
    exit(1)
	
utc = pytz.utc

class EventManager :
	events = (("The Folk ARPS Sunday Session", 6, 17, 20), ("The Folk ARPS Tuesday Session", 1, 17, 20))
	warnings = ((" starts in five hours!", datetime.timedelta(hours=5)),(" starts in two hours!", datetime.timedelta(hours=2)),(" starts in thirty minutes!",datetime.timedelta(minutes=30)),(" is starting!", datetime.timedelta(0)))
	timezone = pytz.timezone("Europe/London")
	nextEvent = None;
	timer = None;
	channels = ["107862710267453440"]
	
	def handleMessage(self, client) :
		if (self.timer is None) :
			self.findNextEvent()
			if (self.nextEvent is not None) :
				for warning in self.warnings :
					if (self.nextEvent[1] - warning[1] > utc.localize(datetime.datetime.utcnow())) :
						seconds = (self.nextEvent[1] - warning[1] - utc.localize(datetime.datetime.utcnow())).total_seconds();
						self.timer = threading.Timer(seconds, self.handleTimer, args=[client, self.nextEvent[0] + warning[0]])
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
		

manager = EventManager()	

@client.event
def on_ready():
    print('Connected!')
    print('Username: ' + client.user.name)
    print('ID: ' + client.user.id)

@client.event
def on_message(message):
	manager.handleMessage(client)
	if (message.content == "!status") :
		client.send_message(message.channel, "Working. Probably.")
	if (message.content == "!nextevent") :
		client.send_message(message.channel, "Next event is " + manager.nextEvent[0] + " at " + str(manager.nextEvent[1]))
	if (message.content == "!armaserver") :
		client.send_message(message.channel, "server.folkarps.com:2702")
	if (message.content == "!testserver") :
		client.send_message(message.channel, "server.folkarps.com:2722")
	if (message.content == "!tsserver") :
		client.send_message(message.channel, "server.folkarps.com:9988")
	if (message.content == "!help") :
		client.send_message(message.channel, "Available commands: !armaserver, !testserver, !tsserver, !nextevent, !status")

client.run()