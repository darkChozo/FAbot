# -*- coding: utf-8 -*-
import ConfigParser
import json


class ConfigManager(object):
    def __init__(self, path):
        self.parser = ConfigParser.ConfigParser()
        self.parser.read("config.ini")

    def get(self, key, section="Config", default=None):
        try:
            value = self.parser.get(section, key)
        except ConfigParser.NoSectionError:
            msg = "Warning, section {} not found in config.ini. Value {} set to {}".format(section, key, default)
            print msg
        except ConfigParser.NoOptionError:
            msg = "Warning, option {} not found in config.ini. Set to {}".format(key, default)
            print msg
        except:
            raise
        else:
            return value
        return default

    def get_json(self, key, section="Config", default=None):
        value = self.get(key, section=section)
        if value is None:
            return default
        return json.loads(value)