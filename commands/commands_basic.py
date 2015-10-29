# -*- coding: utf-8 -*-
from .command import command, commands


@command('help')
def help_cmd(message, args):
    """!help : display this text"""
    if not args:  # We don't want to spam chat because someone wanted to sing The Beatles in Spanish, do we?
        help_texts = ["Available commands:"]
        for item in commands.values():
            if item.func_doc:
                help_texts.append(item.func_doc)
        msg = '\n'.join(help_texts)
        return msg


@command('github')
def github(message, args):
    """!github : report the URL of the FA_bot github project"""
    return "https://github.com/darkChozo/folkbot"
