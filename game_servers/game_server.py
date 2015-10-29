# -*- coding: utf-8 -*-
import string
import valve.source.a2s


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