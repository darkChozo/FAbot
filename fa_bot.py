#!/usr/local/bin/python
import logging
import ConfigParser
import json
from discord_client import main_client
import event_manager
import game_servers


class FAbot(object):

    @staticmethod
    def start():
        # Logging
        logging.basicConfig(filename="FA_bot.log", level=logging.DEBUG, format="%(asctime)-15s %(message)s")
        logging.info("FAbot starting up")

        # Configuration file
        logging.info("Reading configuration")
        config = ConfigParser.RawConfigParser()
        config.read("config.ini")

        client_email = config.get("Config", "email")
        client_pass = config.get("Config", "password")
        event_manager.announcement_channels = json.loads(config.get("Config", "announcement_channels"))

        main_client.channel_whitelist = json.loads(config.get("Config", "channel_whitelist"))
        main_client.announcement_channels = json.loads(config.get("Config", "announcement_channels"))
        main_client.send_welcome_pm = config.getboolean("Config", "send_welcome_pm")
        main_client.make_join_announcment = config.getboolean("Config", "make_join_announcment")
        main_client.make_leave_announcment = config.getboolean("Config", "make_leave_announcment")

        # Game servers
        game_servers.game_servers['arma'] = game_servers.ArmaServer(
            ip=config.get("Config", "arma_server_ip"),
            port=int(config.get("Config", "arma_server_port"))
        )
        game_servers.game_servers['insurgency'] = game_servers.InsurgencyServer(
            ip=config.get("Config", "insurgency_server_ip"),
            port=int(config.get("Config", "insurgency_server_port"))
        )

        # Discord client
        logging.info("Logging into Discord")
        main_client.login(client_email, client_pass)

        if not main_client.is_logged_in:
            logging.critical("Logging into Discord failed")
            print('Logging in to Discord failed')
            exit(1)

        logging.info("Entering main message event loop")
        main_client.run()


# Full sail ahoy!
if __name__ == '__main__':
    try:
        FAbot.start()
    except KeyboardInterrupt:
        print "Disconnecting..."
        logging.info("Keyboard interrupt. Disconnecting.")
        main_client.logout()
