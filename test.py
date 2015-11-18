import unittest
from bot.commands import commands
from bot import event_manager
from bot import game_server

class FakeClient(object):
    def send_message(self,channel,message):
        "empty";

class FakeBot(object):
    def __init__(self, **kwargs):
        self.game_servers = {}
        self.commands = commands
        self.event_manager = kwargs.get("event_manager")
        self.main_watcher = kwargs.get("main_watcher")
        self.FAMDB_app_id = kwargs.get("FAMDB_app_id")
        self.FAMDB_API_key = kwargs.get("FAMDB_API_key")
        self.TS3_address = kwargs.get("TS3_address")
        self.TS3_port = kwargs.get("TS3_port")
        self.TS3_password = kwargs.get("TS3_password")

    def server_address(self, server_name):
        return "wow this function sure is fake"

class FakeMessage(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.server = kwargs.get("server")

class FakeChannel(object):
    def __init__(self, **kwargs):
        self.channel = kwargs.get("channel")

class FakeSession(object):
    isSetVar = False;
    def start(self) :
        self.isSetVar = True

    def stop(self) :
        self.isSetVar = False

    def isSet(self) :
        return self.isSetVar

class FakeWatcher(object):
    session = FakeSession()

    def start(self):
        self.session.start()

    def stop(self):
        self.session.stop()

class TestCommands(unittest.TestCase):
    def setUp(self):
        self.main_client = FakeClient();
        self.bot = FakeBot(
            # this may fail and/or cause weird issues if run when a event starts
            event_manager = event_manager.EventManager(),
            main_watcher = FakeWatcher(),
            FAMDB_app_id = "1IijmSndIGJFPg6cw6xDl5PRe5AiGCHliyPzIgPc",
            FAMDB_API_key = "A7n2hKn8S1qiBY3dmSduYl90kskHBi957KXuSqgs",
            TS3_address = "server.folkarps.com",
            TS3_port = 9988,
            TS3_password = "freedom"
        )
        self.test_channel = FakeMessage(id = "12345", name = "Test Channel", server = "Test Server")
        self.test_message = FakeChannel(channel = self.test_channel)
        self.bot.game_servers['arma'] = game_server.ArmaServer(
            ip="91.121.223.212",
            port=2702,
            password="freedom"
        )
        self.bot.game_servers['armatest'] = game_server.ArmaServer(
            ip="91.121.223.212",
            port=2722,
            password="freedom"
        )
        self.bot.game_servers['insurgency'] = game_server.InsurgencyServer(
            ip="91.121.223.212",
            port=27014
        )

    def tearDown(self):
        self.bot.event_manager.stop();

    #update once status works
    def test_status(self):
        self.assertIsNotNone(commands["status"](self.bot, self.test_message, ""));

    def test_info(self):
        self.assertRegexpMatches(commands["info"](self.bot, self.test_message, ""), "Arma 3 v[0-9\.]* - Folk ARPS - .* - [0-9]*/[0-9]* humans, [0-9]* AI on .*")

    def test_github(self):
        self.assertEqual(commands["github"](self.bot, self.test_message, ""), "https://github.com/darkChozo/folkbot")

    def test_help(self):
        self.assertRegexpMatches(commands["help"](self.bot, self.test_message, ""), "Available commands:\n(!(\w )+: .*)*");

    def test_tsserver(self):
        self.assertEqual(commands["tsserver"](self.bot, self.test_message, ""), "Our Teamspeak server:\nAddress: **server.folkarps.com:9988** Password: **freedom**\nOr you can just click this link:\n<ts3server://server.folkarps.com/?port=9988&password=freedom>");

    def test_testserver(self):
        self.assertEqual(commands["testserver"](self.bot, self.test_message, ""), "wow this function sure is fake");

    def test_armaserver(self):
        self.assertEqual(commands["armaserver"](self.bot, self.test_message, ""), "wow this function sure is fake");

    def test_insurgency(self):
        self.assertRegexpMatches(commands["insurgency"](self.bot, self.test_message, ""), "Insurgency v[0-9\.]* - .* - .* - [0-9]*/[0-9]* humans, [0-9]* AI on .*")

    def test_ping(self):
        self.assertRegexpMatches(commands["ping"](self.bot, self.test_message, ""), "[0-9.]* milliseconds")

    def test_nextevent(self):
        self.bot.event_manager.handle_message(self.main_client)
        self.assertRegexpMatches(commands["nextevent"](self.bot, self.test_message, ""), "Next event is .+ in .+ \([0-9]+:[0-9]+ UTC on .+\)\.")

    def test_players(self):
        self.assertRegexpMatches(commands["players"](self.bot, self.test_message, ""), "Total players: [0-9]+(\n[0-9]+ .* \(on for [0-9]+\.[0.9]+ seconds\))*$")

    def test_players_insurgency(self):
        self.assertRegexpMatches(commands["players"](self.bot, self.test_message, "insurgency"), "Total players: [0-9]+(\n[0-9]+ .* \(on for [0-9]+\.[0.9]+ seconds\))*$")

    #update once rules works
    def test_rules(self):
        self.assertIsNotNone(commands["rules"](self.bot, self.test_message, ""));

    def test_insurgency(self):
        self.assertRegexpMatches(commands["insurgency"](self.bot, self.test_message, ""), "Insurgency v[0-9\.]* - Folk ARPS - Insurgency - [0-9]*/[0-9]* humans, [0-9]* AI on .*")

    def test_f3(self):
        self.assertEqual(commands["f3"](self.bot, self.test_message, ""), "Latest F3 downloads: http://ferstaberinde.com/f3/en//index.php?title=Downloads");

    def test_biki(self):
        self.assertEqual(commands["biki"](self.bot, self.test_message, "search"), "https://community.bistudio.com/wiki?search=search&title=Special%3ASearch&go=Go");

    def test_f3wiki(self):
        self.assertEqual(commands["f3wiki"](self.bot, self.test_message, "search"), "http://ferstaberinde.com/f3/en//index.php?search=search&title=Special%3ASearch&go=Go");

    def test_session(self):
        self.assertIsNone(commands["session"](self.bot, self.test_message, "start"));
        self.assertEqual(commands["session"](self.bot, self.test_message, ""), "Folk ARPS session underway; FA_bot will announce when we're slotting");
        self.assertIsNone(commands["session"](self.bot, self.test_message, "stop"));
        self.assertEqual(commands["session"](self.bot, self.test_message, ""), "No Folk ARPS session running at the moment. Check when the next event is on with !nextevent");

    def test_addons(self):
        self.assertEqual(commands["addons"](self.bot, self.test_message, ""), "http://www.folkarps.com/forum/viewtopic.php?f=43&t=1382");

    def test_test(self):
        # i dunno
        self.assertIsNotNone(commands["test"](self.bot, self.test_message, ""));

    def test_mission_current(self):
        self.assertRegexpMatches(commands["mission"](self.bot, self.test_message, ""), "\*\*Mission name: .*\*\* \*.*\*\n\*\*Mission type:\*\* .*\n*\*Location:\*\* .*\n*\*Author:\*\* .*\n*\*Description:\*\* .*");

    def test_mission_search(self):
        self.assertRegexpMatches(commands["mission"](self.bot, self.test_message, "Bees"), "\*\*Mission name: .*\*\*\n \*\*Mission type:\*\* .*\n\*\*Location:\*\* .*\n\*\*Author:\*\* .*\n\*\*Description:\*\* [.\n]*");

    # this will be an interesting one...
    #def test_update(self)

if __name__ == '__main__':
    unittest.main()
