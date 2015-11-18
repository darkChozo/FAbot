# -*- coding: utf-8 -*-
from .command import command, commands
import logging

@command('help')
def help_cmd(bot, message, args):
    """!help : display this text"""
    # We don't want to spam chat because someone wanted
    # to sing The Beatles in Spanish, do we?
    if not args:
        help_texts = ["Available commands:"]
        for item in bot.commands.values():
            if item.func_doc:
                help_texts.append(item.func_doc)
        msg = '\n'.join(help_texts)
        return msg

@command('github')
def github(bot, message, args):
    """!github : report the URL of the FA_bot github project"""
    if message is None:
        return None
    return "https://github.com/darkChozo/folkbot"