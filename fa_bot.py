#!/usr/local/bin/python
import bot
import logging

# Full sail ahoy!
if __name__ == '__main__':
    fa_bot = bot.FAbot.FAbot("config.ini")
    try:
        fa_bot.start()
    except KeyboardInterrupt:
        print "Disconnecting..."
        logging.info("Keyboard interrupt. Disconnecting.")
        fa_bot.stop()
