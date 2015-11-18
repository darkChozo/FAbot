#!/usr/local/bin/python
import logging
import re
import discord_client
import config_manager
import event_manager
import game_server
import watcher
import requests
import json
import subprocess
from urllib import quote
import commands

class FAbot(object):
    def __init__(self, configfilename):
        self.client_email = None
        self.client_pass = None
        self.discordClient = None
        self.event_manager = None
        self.main_watcher = None
        self.game_servers = {}
        self.commandregex = re.compile("(?s)^!(?P<command>\w+)\s*(?P<args>.*)?")
        self.commands = commands.commands
        self.FAMDB_API_key = None
        self.FAMDB_app_id = None
        self.TS3_address = None
        self.TS3_port = None
        self.TS3_password = None

        # Logging
        logging.basicConfig(filename="log/FA_bot.log", level=logging.DEBUG,
                            format="%(asctime)-15s %(message)s")
        logging.info("FAbot starting up")
        logging.info("Registering commands: ")

        logging.info("Full command list:")
        logging.info(self.commands)

        # Configuration file
        logging.info("Reading configuration")
        self.config = config_manager.ConfigManager(configfilename)

    def start(self):
        self.event_manager = event_manager.EventManager()
        self.main_watcher = watcher.Watcher(self)

        self.event_manager.announcement_channels = self.config.get_json("announcement_channels", default=[])

        # TODO: probably event manager should take channels from client instead?

        # Game servers
        # see how regular this names are, it's asking for the loop
        self.game_servers['arma'] = game_server.ArmaServer(
            ip=self.config.get("arma_server_ip", section="Game Servers"),
            port=self.config.get("arma_server_port", section="Game Servers"),
            password=self.config.get("arma_server_password", section="Game Servers")
        )
        self.game_servers['arma_test'] = game_server.ArmaServer(
            ip=self.config.get("arma_test_server_ip", section="Game Servers"),
            port=self.config.get("arma_test_server_port", section="Game Servers"),
            password=self.config.get("arma_test_server_password", section="Game Servers")
        )
        self.game_servers['insurgency'] = game_server.InsurgencyServer(
            ip=self.config.get("insurgency_server_ip", section="Game Servers"),
            port=self.config.get("insurgency_server_port", section="Game Servers"),
            password=self.config.get("insurgency_server_password", section="Game Servers")
        )

        # TS3
        self.TS3_address = self.config.get("teamspeak_server_ip", section="Communication Servers")
        self.TS3_port = self.config.get("teamspeak_server_port", section="Communication Servers")
        self.TS3_password = self.config.get("teamspeak_server_password", section="Communication Servers")

        # FAMDB
        self.FAMDB_API_key = self.config.get("API_key", section="FAMDB")
        self.FAMDB_app_id  = self.config.get("application_id", section="FAMDB")

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

        if self.client_email is None or self.client_pass is None:
            logging.critical("Could not find Discord authentication details "
                             "in config file.")
            print("Could not find Discord authentication details.")
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

    def server_address(self, server_name):
        if server_name in self.game_servers:
            server = self.game_servers[server_name]
            address_msg = "Address:  **{}**, Port: **{}**".format(server.ip, server.port)
            password_msg = "\nPassword: **{}**".format(server.password) if server.password is not None else ""
            steam_url = "steam://connect/{}:{}/".format(server.ip, server.port + 1)  # Steamworks port is one higher
            if server.password is not None:
                steam_url = "{}{}".format(steam_url, server.password)
            return "{}{}\nOr just use this link:\n<{}>".format(address_msg, password_msg, steam_url)

    def stop(self):
        self.discordClient.logout()
        self.event_manager.stop()
        self.main_watcher.stop()
