# -*- coding: utf-8 -*-
from .command import command
from game_servers import game_servers
from event_manager import event_manager


@command('status')
def status(message, args):
    """!status : reports the current state of the game on the Arma 3 server"""
    gametype, gamestate = game_servers['arma'].state()
    return gamestate


@command('nextevent')
def nextevent(message, args):
    """!nextevent : reports the next scheduled Folk ARPS session"""
    return event_manager.next_event_message()


@command('armaserver')
def armaserver(message, args):
    """!armaserver : report the hostname and port of the Folk ARPS Arma server"""
    return "server.folkarps.com:2702"


@command('testserver')
def testserver(message, args):
    """!testserver : report the hostname and port of the Folk ARPS mission testing Arma server"""
    return "server.folkarps.com:2722"


@command('tsserver')
def tsserver(message, args):
    """!tsserver : report the hostname and port of the Folk ARPS teamspeak server"""
    return "server.folkarps.com:9988"


@command('ping')
def ping(message, args):
    """!ping : report the ping time from FA_bot to the Arma server"""
    ping = game_servers['arma'].ping()
    return "{} milliseconds".format(str(ping))


@command('info')
def info(message, args):
    """!info : report some basic information on the Arma server"""
    info = game_servers['arma'].info()
    msg = "Arma 3 v{version} - {server_name} - {game} - {player_count}/{max_players} humans, {bot_count} AI on {map}"
    return msg.format(**info)


@command('players')
def players(message, args):
    """!players (insurgency) : show a list of players on the Arma (Insurgency) server"""
    if args == "insurgency":
        players = game_servers['insurgency'].players()
    else:
        players = game_servers['arma'].players()
    player_string = "Total players: {player_count}\n".format(**players)
    for player in sorted(players["players"], key=lambda p: p["score"], reverse=True):
        player_string += "{score} {name} (on for {duration} seconds)\n".format(**player)
    return player_string


@command('rules')
def rules(message, args):
    """!rules : report on the cvars in force on the insurgency server"""
    # rules doesn't work for the arma server for some reason
    rules = game_servers['insurgency'].rules()
    msg = rules["rule_count"] + " rules:\n"
    msg += "\n".join(rules["rules"])
    return msg


@command('insurgency')
def insurgency(message, args):
    """!insurgency : report on the current state of the Folk ARPS Insurgency server"""
    msg = "Insurgency v{version} - {server_name} - {game} - {player_count}/{max_players} humans, {bot_count} AI on {map}"
    info = game_servers['insurgency'].info()
    return msg.format(**info)


@command('f3')
def f3(message, args):
    """!f3 : report the URL for the latest F3 release"""
    return "Latest F3 downloads: http://ferstaberinde.com/f3/en//index.php?title=Downloads"


@command('biki')
def biki(message, args):
    """!biki <term> : search the bohemia interactive wiki for <term>"""
    if args is not None:
        return "https://community.bistudio.com/wiki?search={}&title=Special%3ASearch&go=Go".format(
            "+".join(args.split()))


@command('f3wiki')
def f3wiki(message, args):
    """!f3wiki <term> : search the f3 wiki for <term>"""
    if args is not None:
        return "http://ferstaberinde.com/f3/en//index.php?search={}&title=Special%3ASearch&go=Go".format(
            "+".join(args.split()))


@command('addons')
def addons(message, args):
    """!addons : display link to FA optional addons"""
    return "http://www.folkarps.com/forum/viewtopic.php?f=43&t=1382"


@command('test')
def test(message, args):
    # """!test : under development"""
    msg = game_servers['arma'].raw_info() + '\n\n' + game_servers['insurgency'].raw_info()
    return msg
