# -*- coding: utf-8 -*-
import logging
import discord


class Client(discord.Client):
    bot = None

    def __init__(self, bot):
        super(Client, self).__init__()
        self.channel_whitelist = []
        self.announcement_channels = []
        self.welcome_pm = None
        self.join_announcement = None
        self.leave_announcement = None
        self.bot = bot

    def on_ready(self):
        print('connected!')
        print('username: ' + self.user.name)
        print('id: ' + self.user.id)
        logging.info("connected to discord as %s (id: %s)",
                     self.user.name, self.user.id)

    def on_message(self, message):
        self.bot.event_manager.handle_message(self)
        if message.content[0] == "!":
            if (len(self.channel_whitelist) > 0 and
                    message.channel.id not in self.channel_whitelist):
                return
            if not message.channel.is_private:
                logging.info("#%s (%s) : %s", message.channel.name,
                             message.author.name, message.content)
            else:
                logging.info("%s : %s", message.author.name, message.content)
            cmdline = self.bot.commandregex.search(message.content.lower())
            logging.debug("Command parsed : %s(%s)", cmdline.group('command'),
                          cmdline.group('args'))
            if cmdline.group('command') in self.bot.commands:
                msg = self.bot.commands[cmdline.group('command')](self.bot,
                                                                  message,
                                                                  cmdline.group('args'))
                if msg is not None:
                    self.send_message(message.channel, msg)

    def on_member_join(self, server, member):
        if self.welcome_pm:
            self.send_message(member, self.welcome_pm)
        if self.join_announcement:
            for channel_number in self.announcement_channels:
                channel = self.get_channel(channel_number)
                if channel.server.id == server.id:
                    self.send_message(channel, self.join_announcement)

    def on_member_remove(self, server, member):
        if self.leave_announcement:
            for channel_number in self.announcement_channels:
                channel = self.get_channel(channel_number)
                if channel.server.id == server.id:
                    self.send_message(channel, self.leave_announcement)
