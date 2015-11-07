#!/usr/local/bin/python
import bot
import logging

# Full sail ahoy!
if __name__ == '__main__':
    fa_bot = bot.FAbot.FAbot("config.ini")
    try:
        fa_bot.start()
    except KeyboardInterrupt:
        print "Disconnecting... Might take up to 60 seconds because of reasons."  # TODO: These are known reasons.
        logging.info("Keyboard interrupt. Disconnecting.")
        fa_bot.stop()
