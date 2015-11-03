#!/usr/local/bin/python
import logging
from config_manager import ConfigManager
from discord_client import main_client
from event_manager import event_manager
import game_servers
from variables_manager import variables_manager


class FAbot(object):

    @staticmethod
    def start():
        # Logging
        logging.basicConfig(filename="FA_bot.log", level=logging.DEBUG, format="%(asctime)-15s %(message)s")
        logging.info("FAbot starting up")

        # Configuration file
        logging.info("Reading configuration")
        config = ConfigManager("config.ini")

        client_email = config.get("email", section="Bot Account")
        client_pass = config.get("password", section="Bot Account")
        event_manager.announcement_channels = config.get_json("announcement_channels", default=[])
        # TODO: probably event manager should take channels from client instead?

        main_client.channel_whitelist = config.get_json("channel_whitelist", default=[])
        main_client.announcement_channels = config.get_json("announcement_channels", default=[])

        main_client.welcome_pm = config.get("welcome_pm", section="Announcements")
        main_client.join_announcement = config.get("join_announcement", section="Announcements")
        main_client.leave_announcement = config.get("leave_announcement", section="Announcements")

        # Game servers
        game_servers.game_servers['arma'] = game_servers.ArmaServer(
            ip=config.get("arma_server_ip"),
            port=int(config.get("arma_server_port"))
        )
        game_servers.game_servers['insurgency'] = game_servers.InsurgencyServer(
            ip=config.get("insurgency_server_ip"),
            port=int(config.get("insurgency_server_port"))
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
