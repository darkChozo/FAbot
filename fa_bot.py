#!/usr/local/bin/python
import logging
import re
import discord_client
import config_manager
import event_manager
import game_server
import watcher
import command

class FAbot(object):
    discordClient = None
    event_manager = None
    main_watcher = None
    game_servers = {}
    commandregex = re.compile("(?s)^!(?P<command>\w+)\s*(?P<args>.*)?")
    commands = {}

    @classmethod
    def command(self,cmd):
        """
        When you write a new command, add this decorator to it, so it gets registered
        """
        def wrapper(self,cmd):
            self.commands[cmd] = args[0]
            return args[0]
        return wrapper

    def __init__(self):
        # Logging
        logging.basicConfig(filename="logs/FA_bot.log", level=logging.DEBUG, format="%(asctime)-15s %(message)s")
        logging.info("FAbot starting up")

    def start(self):
        # Configuration file
        logging.info("Reading configuration")
        self.config = config_manager.ConfigManager("config.ini")

        self.event_manager = event_manager.EventManager()
        self.main_watcher = watcher.Watcher(self)

        self.event_manager.announcement_channels = self.config.get_json("announcement_channels", default=[])
        # TODO: probably event manager should take channels from client instead?

        # Game servers
        self.game_servers['arma'] = game_server.ArmaServer(
            ip=self.config.get("arma_server_ip"),
            port=int(self.config.get("arma_server_port"))
        )
        self.game_servers['insurgency'] = game_server.InsurgencyServer(
            ip=self.config.get("insurgency_server_ip"),
            port=int(self.config.get("insurgency_server_port"))
        )

        # Discord client
        logging.info("Logging into Discord")
        self.discordClient = discord_client.Client(self)

        self.discordClient.channel_whitelist = self.config.get_json("channel_whitelist", default=[])
        self.discordClient.announcement_channels = self.config.get_json("announcement_channels", default=[])

        self.discordClient.welcome_pm = self.config.get("welcome_pm", section="Announcements")
        self.discordClient.join_announcement = self.config.get("join_announcement", section="Announcements")
        self.discordClient.leave_announcement = self.config.get("leave_announcement", section="Announcements")

        self.client_email = self.config.get("email", section="Bot Account")
        self.client_pass = self.config.get("password", section="Bot Account")
        if self.client_email == None or self.client_pass == None:
            logging.critical("Could not find Discord authentication details in config file.")
            print("Could not find Discord authentication details in config file.")
            exit(1)

        self.discordClient.login(self.client_email, self.client_pass)

        if not self.discordClient.is_logged_in:
            logging.critical("Logging into Discord failed")
            print('Logging in to Discord failed')
            exit(1)

        logging.info("Starting main watcher")
        self.main_watcher.start()

        logging.info("Entering main message event loop")
        self.discordClient.run()



# Full sail ahoy!
if __name__ == '__main__':
    try:
        fa_bot = FAbot()

        fa_bot.start()
    except KeyboardInterrupt:
        print "Disconnecting..."
        logging.info("Keyboard interrupt. Disconnecting.")
        fa_bot.discordClient.logout()
