# -*- coding: utf-8 -*-
import time
import threading
import logging


def watch_arma_server(watcher, delay):
    """
    While session is set, check the Arma server.
    :param watcher:
    :param delay: Time to wait between checks.
    :return:
    """
    logging.info('Arma Server watcher thread starting')
    time.sleep(3)
    start_time = time.time()
    while watcher.session.isSet():
        if time.time() - start_time >= delay:
            start_time = time.time()
            gametype, gamestatetext, gamestate = watcher.bot.game_servers['arma'].state()
            logging.info('Arma server state: %s', gamestatetext)

            if gamestate != watcher.armaState:
                if gamestate == 3:
                    logging.info('Arma server entering slotting state')
                    for channel in watcher.bot.discordClient.announcement_channels:
                        watcher.bot.discordClient.send_message(
                            watcher.bot.discordClient.get_channel(channel),
                            "Arma server is now slotting for the next mission..."
                        )
                if watcher.armaState == 3:
                    logging.info('Arma server leaving slotting state')
                    for channel in watcher.bot.discordClient.announcement_channels:
                        watcher.bot.discordClient.send_message(
                            watcher.bot.discordClient.get_channel(channel),
                            "Slotting for the next mission on the Arma server has closed..."
                        )
            watcher.armaState = gamestate

        time.sleep(1)
    logging.info('Arma Server watcher thread ending')


class Watcher(object):
    armaState = 0  # Why is that static?
    bot = None  # Why is that static?

    def __init__(self, fabot):
        self.bot = fabot
        self.session = threading.Event()
        self.watcherThread = None

    def start(self):
        logging.info('Trying to start Arma Server watcher thread')
        self.session.set()
        self.watcherThread = threading.Thread(
            name='Watch Arma Server',
            target=watch_arma_server,
            args=(self, 60)
        )
        self.watcherThread.start()

    def stop(self):
        logging.info('Trying to stop Arma Server watcher thread')
        self.session.clear()
