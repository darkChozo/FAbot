# -*- coding: utf-8 -*-
import ConfigParser
import json


class ConfigManager(object):
    def __init__(self, path):
        self.parser = ConfigParser.ConfigParser()
        self.parser.read("config.ini")

    def get(self, key, section="Config"):
        try:
            value = self.parser.get(section, key)
        except ConfigParser.NoSectionError:
            msg = "Warning, section {} not found in config.ini. Value {} set to None".format(section, key)
            print msg
        except ConfigParser.NoOptionError:
            msg = "Warning, option {} not found in config.ini. Set to None".format(key)
            print msg
        except:
            raise
        else:
            return value
        return None

    def get_json(self, key, section="Config"):
        value = self.get(key, section=section)
        return json.loads(value)

    def get_bool(self, key, section="Config"):
        value = self.get(key, section=section)
        return bool(value)

    def get_float(self, key, section="Config"):
        value = self.get(key, section=section)
        return float(value)

    def get_int(self, key, section="Config"):
        value = self.get(key, section=section)
        return int(value)
