# -*- coding: utf-8 -*-


class VariablesManager(object):
    def __init__(self):
        pass

    def get_variables(self, channel=None, client=None, member=None, message=None, server=None, user=None):
        variables = dict()

        server_name = self.server_name(channel=channel, member=member, message=message, server=server)
        if server_name is not None:
            variables['server_name'] = server_name

        user_name = self.user_name(member=member, message=message, user=user)
        if user_name is not None:
            variables['user_name'] = user_name

        bot_name = self.bot_name(client=client)
        if bot_name is not None:
            variables['bot_name'] = bot_name

        return variables

    @staticmethod
    def server_name(channel=None, member=None, message=None, server=None):
        if server is None:
            if channel is not None:
                server = channel.server
            elif member is not None:
                server = member.server
            elif message is not None:
                server = message.channel.server
            else:
                return None
        return server.name

    @staticmethod
    def user_name(member=None, message=None, user=None):
        if user is None:
            if member is not None:
                user = member
            elif message is not None:
                user = message.author
            else:
                return None
        return user.name

    @staticmethod
    def bot_name(client=None):
        if client is None:
            return None
        return client.connection.user.name

variables_manager = VariablesManager()
