# -*- coding: utf-8 -*-
from .command import command, commands
import logging
import json
import re
import requests

@command('status')
def status(bot, message, args):
    """!status : reports the current state of the game on the Arma server"""
    if message is None:
        return None
    gametype, gamestate = bot.game_servers['arma'].state()
    return gamestate

@command('nextevent')
def nextevent(bot, message, args):
    """!nextevent : reports the next scheduled Folk ARPS session"""
    if message is None:
        return None
    return bot.event_manager.next_event_message()

@command('armaserver')
def armaserver(bot, message, args):
    """!armaserver : report the hostname and port of the Folk ARPS Arma server"""
    if message is None:
        return None
    return bot.server_address("arma")

@command('testserver')
def testserver(bot, message, args):
    """!testserver : report the hostname and port of the Folk ARPS mission testing Arma server"""
    if message is None:
        return None
    return bot.server_address("arma_test")

@command('insurgencyserver')
def insurgencyserver(bot, message, args):
    """!insurgencyserver : report the hostname and port of the Folk ARPS Insurgency (Standalone) server"""
    if message is None:
        return None
    return bot.server_address("insurgency")

@command('tsserver')
def tsserver(bot, message, args):
        """!tsserver : report the hostname and port of the Folk ARPS teamspeak server"""
        if message is None:
            return None
        if not bot.TS3_address or not bot.TS3_port:
            return "I don't know about any TS3 Server."

        # nickname = "&nickname={}".format(quote(message.author.name))
        nickname = ""

        ts3_link = "ts3server://{}/?port={}{}".format(bot.TS3_address, bot.TS3_port, nickname)
        password_text = ""
        if bot.TS3_password is not None:
            ts3_link = "{}&password={}".format(ts3_link, bot.TS3_password)
            password_text = " Password: **{}**".format(bot.TS3_password)

        msg = "Our Teamspeak server:\nAddress: **{}:{}**{}\nOr you can just click this link:\n<{}>".format(
            bot.TS3_address, bot.TS3_port, password_text, ts3_link)
        return msg

@command('ping')
def ping(bot, message, args):
    """!ping : report the ping time from FA_bot to the Arma server"""
    if message is None:
        return None
    ping = bot.game_servers['arma'].ping()
    return "{} milliseconds".format(str(ping))

@command('info')
def info(bot, message, args):
    """!info : report some basic information on the Arma server"""
    if message is None:
        return None
    info = bot.game_servers['arma'].info()
    msg = "Arma 3 v{version} - {server_name} - {game} - {player_count}/{max_players} humans, {bot_count} AI on {map}"
    return msg.format(**info)

@command('players')
def players(bot, message, args):
    """!players (insurgency) : show a list of players on the Arma (Insurgency) server"""
    if message is None:
        return None
    if args == "insurgency":
        players = bot.game_servers['insurgency'].players()
    else:
        players = bot.game_servers['arma'].players()
    player_string = "Total players: {player_count}\n".format(**players)
    for player in sorted(players["players"],
                         key=lambda p: p["score"],
                         reverse=True):
        player_string += "{score} {name} (on for {duration} seconds)\n".format(**player)
    return player_string

@command('rules')
def rules(bot, message, args):
    """!rules : report on the cvars in force on the insurgency server"""
    if message is None:
        return None
    # rules doesn't work for the arma server for some reason
    rules = bot.game_servers['insurgency'].rules()
    msg = rules["rule_count"] + " rules:\n"
    msg += "\n".join(rules["rules"])
    return msg

@command('insurgency')
def insurgency(bot, message, args):
    """!insurgency : report on the current state of the Folk ARPS Insurgency server"""
    if message is None:
        return None
    msg = "Insurgency v{version} - {server_name} - {game} - {player_count}/{max_players} humans, {bot_count} AI on {map}"
    info = bot.game_servers['insurgency'].info()
    return msg.format(**info)

@command('f3')
def f3(bot, message, args):
    """!f3 : report the URL for the latest F3 release"""
    if message is None:
        return None
    return "Latest F3 downloads: http://ferstaberinde.com/f3/en//index.php?title=Downloads"

@command('biki')
def biki(bot, message, args):
    """!biki <term> : search the bohemia interactive wiki for <term>"""
    if message is None:
        return None
    if args is not None:
        return "https://community.bistudio.com/wiki?search={}&title=Special%3ASearch&go=Go".format("+".join(args.split()))

@command('f3wiki')
def f3wiki(bot, message, args):
    """!f3wiki <term> : search the f3 wiki for <term>"""
    if message is None:
        return None
    if args is not None:
        return "http://ferstaberinde.com/f3/en//index.php?search={}&title=Special%3ASearch&go=Go".format("+".join(args.split()))

@command('session')
def session(bot, message, args):
    """!session  : show whether or not a Folk ARPS session is running
    !session start : tell the bot a Folk ARPS session is starting
    !session stop : tell the bot a Folk ARPS session is ending"""
    if message is None:
        return None
    if args == "start":
        bot.main_watcher.start()
    elif args == "stop":
        bot.main_watcher.stop()
    else:
        if bot.main_watcher.session.isSet():
            return "Folk ARPS session underway; FA_bot will announce when we're slotting"
        else:
            return "No Folk ARPS session running at the moment. Check when the next event is on with !nextevent"

@command('addons')
def addons(bot, message, args):
    """!addons : display link to FA optional addons"""
    return "http://www.folkarps.com/forum/viewtopic.php?f=43&t=1382"

@command('test')
def test(bot, message, args):
    # """!test : under development"""
    if message is None:
        return None
    logging.info('test()')
    msg = bot.game_servers['arma'].raw_info() + '\n\n' + bot.game_servers['insurgency'].raw_info()
    return msg

@command('mission')
def mission(bot, message, args):
    """!mission <missionname> : describe <missionname> or the mission currently being played on the server"""
    if message is None:
        return None
    logging.info('mission(%(args)s)' % {'args': args})

    servermapname = None

    if (args is None) or (not args.strip()):
        logging.info('No mission name specified, interrogating arma server')
        servermapname = bot.game_servers['arma'].info()['game']
        regex = re.compile("fa3_[c|a]\w.[0-9]*_(?P<mapname>\w+)[_v[0-9]*]?")
        logging.info('Server map name: %s' % servermapname)
        result = regex.search(servermapname)
        if result.groups is None:
            logging.info("Didn't recognise the server map name")
            return "Need a mission name (didn't recognise the one on the server right now)"
        tokenlist = result.group('mapname').split('_')
        args = max(tokenlist, key=len)
        logging.info('Map name tokens : %s',tokenlist)
        logging.info('Selected search token : %s',args)

    header = {'X-Parse-Application-Id' : bot.FAMDB_app_id,
              'X-Parse-REST-API-Key'   : bot.FAMDB_API_key,
              'Content-Type'           : 'application/json'}

    query = {'where': json.dumps({'missionName' : { '$regex' : '\Q%s\E' % args, '$options' : 'i'}})}
    logging.info('Query: %s' % query)

    response = requests.get('https://api.parse.com/1/classes/Missions', headers=header, params=query)
    logging.info('URL: %s' % response.url)

    result = response.json()
    bestguess = result['results'][0]
    logging.info('Response: %s ' % bestguess)

    data = {'name': bestguess[u'missionName'],
            'type': bestguess[u'missionType'],
            'map':bestguess[u'missionMap'],
            'author':bestguess[u'missionAuthor'],
            'description':bestguess[u'missionDesc']}

    if not servermapname:
        msg = "**Mission name: {name}**\n"
    else:
        msg = "**Mission name: {name}** *({servername})*\n"
        data['servername']=servermapname

    msg = ' '.join( ( msg, "**Mission type:** {type}\n" \
                    "**Location:** {map}\n" \
                    "**Author:** {author}\n" \
                    "**Description:** {description}\n" ) )

    logging.info(msg.format(**data))
    return msg.format(**data)

@command('update')
def update(bot, message, args):
    """!update : tell the bot to get its latest release from github and restart. Permission required."""
    if message is None:
        return None

    try:
        git_result = subprocess.check_output('git pull', shell=True)
        logging.info(git_result)
        if (git_result == 'Already up-to-date.'):
            return git_result

        msg = ' '.join(("**Restarting for update:**\n```", git_result, "```"))
        bot.discordClient.announce(msg)
        open('update','w').close()
        bot.stop()

    except subprocess.CalledProcessError as err:
        logging.info(err)
        logging.info(' '.join(('shell: ', err.cmd)))
        logging.info(' '.join(('output:', err.output)))
        msg = ' '.join(('**Update failed:** ',str(err)))
        return msg