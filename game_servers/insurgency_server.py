# -*- coding: utf-8 -*-
from .game_server import GameServer
import string
import re
import valve.source.a2s


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