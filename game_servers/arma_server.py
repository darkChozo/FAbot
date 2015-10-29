# -*- coding: utf-8 -*-
from .game_server import GameServer
import string
import re
import valve.source.a2s


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
