# -*- coding: utf-8 -*-
import datetime
from pytz import utc, timezone
import threading


class EventManager(object):
    def __init__(self):
        # TODO: Move events to config.ini
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
        self.timezone = timezone("Europe/London")
        self.nextEvent = None
        self.timer = None
        self.announcement_channels = []

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
        for channel in self.announcement_channels:
            cli.send_message(cli.get_channel(channel), message)

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

event_manager = EventManager()
