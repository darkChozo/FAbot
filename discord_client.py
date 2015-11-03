# -*- coding: utf-8 -*-
import logging
import discord
from commands import commandregex, commands
from event_manager import event_manager
from variables_manager import variables_manager


class Client(discord.Client):
    def __init__(self):
        super(Client, self)
        self.channel_whitelist = []
        self.announcement_channels = []
        self.welcome_pm = None
        self.join_announcement = None
        self.leave_announcement = None

main_client = discord.Client()


@main_client.event
def on_ready():
    print('Connected!')
    print('Username: ' + main_client.user.name)
    print('ID: ' + main_client.user.id)
    logging.info("Connected to Discord as %s (ID: %s)", main_client.user.name, main_client.user.id)


@main_client.event
def on_message(message):
    event_manager.handle_message(main_client)
    if message.content[0] == "!":
        if len(main_client.channel_whitelist) > 0 and message.channel.id not in main_client.channel_whitelist:
            return
        if not message.channel.is_private:
            logging.info("#%s (%s) : %s", message.channel.name, message.author.name, message.content)
        else:
            logging.info("%s : %s", message.author.name, message.content)
        cmdline = commandregex.search(message.content.lower())
        logging.debug("Command : %s(%s)", cmdline.group('command'), cmdline.group('args'))
        if cmdline.group('command') in commands:
            msg = commands[cmdline.group('command')](message, cmdline.group('args'))
            if msg is not None:
                variables = variables_manager.get_variables(client=main_client, message=message)
                main_client.send_message(message.channel, msg.format(**variables))


@main_client.event
def on_member_join(server, member):
    if main_client.welcome_pm:
        variables = variables_manager.get_variables(client=main_client, member=member)
        main_client.send_message(member, main_client.welcome_pm.format(**variables))
    if main_client.join_announcement:
        for channel_number in main_client.announcement_channels:
            channel = main_client.get_channel(channel_number)
            if channel.server.id == server.id:
                variables = variables_manager.get_variables(channel=channel, client=main_client, member=member)
                main_client.send_message(channel, main_client.join_announcement.format(**variables))


@main_client.event
def on_member_remove(server, member):
    if main_client.leave_announcement:
        for channel_number in main_client.announcement_channels:
            channel = main_client.get_channel(channel_number)
            if channel.server.id == server.id:
                variables = variables_manager.get_variables(channel=channel, client=main_client, member=member)
                main_client.send_message(channel, main_client.leave_announcement.format(**variables))
