# config.py --- Configuration file support

# Copyright (C) 2010 Jorgen Schaefer <forcer@forcix.cx>

import ConfigParser
import os

CONFIG_FILES = ["/etc/twf.conf",
                os.path.expanduser("~/.twf.conf")]

__all__ = ["DefaultConfigParser"]

class DefaultConfigParser(ConfigParser.SafeConfigParser):
    """
    A ConfigParser object that supports default values.
    """
    def get(self, section, option, default=None):
        try:
            return ConfigParser.SafeConfigParser.get(self, section, option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            if default is not None:
                return default
            else:
                raise

    def getint(self, section, option, default=None):
        try:
            return ConfigParser.SafeConfigParser.getint(self, section, option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            if default is not None:
                return default
            else:
                raise

    def getfloat(self, section, option, default=None):
        try:
            return ConfigParser.SafeConfigParser.getfloat(self, section,
                                                          option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            if default is not None:
                return default
            else:
                raise

    def getboolean(self, section, option, default=None):
        try:
            return ConfigParser.SafeConfigParser.getboolean(self, section,
                                                            option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            if default is not None:
                return default
            else:
                raise

config = DefaultConfigParser()
config.read(CONFIG_FILES)
