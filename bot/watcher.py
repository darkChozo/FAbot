# -*- coding: utf-8 -*-
import time
import threading
import logging

def watchArmaServer(watcher, timeout):
    """While session is set, check the Arma server every timeout seconds"""
    logging.info('Arma Server watcher thread starting')
    time.sleep(3)
    while watcher.session.isSet():
        gametype, gamestatetext, gamestate = watcher.bot.game_servers['arma'].state()
        logging.info('Arma server state: %s', gamestatetext)
        if gamestate!=watcher.armaState:
            if gamestate == 3:
                logging.info('Arma server entering slotting state')
                for channel in watcher.bot.discordClient.announcement_channels:
                    watcher.bot.discordClient.send_message(watcher.bot.discordClient.get_channel(channel), "Arma server is now slotting for the next mission...")


            if watcher.armaState == 3:
                logging.info('Arma server leaving slotting state')
                for channel in watcher.bot.discordClient.announcement_channels:
                    watcher.bot.discordClient.send_message(watcher.bot.discordClient.get_channel(channel), "Slotting for the next mission on the Arma server has closed...")

        watcher.armaState = gamestate
        logging.info("Waiting {} seconds".format(timeout))
        time.sleep(timeout)
    logging.info('Arma Server watcher thread ending')


class Watcher(object):
    armaState = 0
    bot = None

    def __init__(self, fabot):
        self.bot = fabot
        self.session = threading.Event()

    def start(self):
        logging.info('Trying to start Arma Server watcher thread')
        self.session.set()
        self.watcherThread= threading.Thread(name='Watch Arma Server',
                            target=watchArmaServer,
                            args=(self, 60))
        self.watcherThread.start()

    def stop(self):
        logging.info('Trying to stop Arma Server watcher thread')
        self.session.clear()

