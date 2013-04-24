#!/usr/bin/env python3

import logging
from logging import *

global __loggers__
global __format__

__loggers__ = {}
__format__ = "[%(levelname)s] %(name)s: %(message)s"

class Logger(logging.Logger):
    def __init__(self, name="root", loglevel=logging.WARNING):
        """
            We derivate the logger class in order to provide easily the
            logging functions (debug, info, etc...), but this requires
            instanciating the member variables ourselves.
        """
        super().__init__(name, loglevel)

        self.handlers = []
        self.filters = []
        self.level = loglevel
        self.name = name
        self.disabled = False
        self.propagate = True
        self.parent = None #logging.getLogger(name)

        # Adds self to loggers map
        if name not in __loggers__:
            __loggers__[name] = self

        # Now for the initialization of our module logger
        formatter = logging.Formatter(__format__)
        self.default_handler = logging.StreamHandler()
        self.default_handler.setFormatter(formatter)
        self.default_handler.setLevel(loglevel)
        self.addHandler(self.default_handler)
        super().addHandler(self.default_handler)
        logging.getLogger(name).addHandler(self.default_handler)
        return

    def setFormat(self, fmt):
        """
            This function changes the output format of the module logger
        """
        formatter = logging.Formatter(fmt)
        self.default_handler.setFormatter(formatter)

    def setLevel(self, lvl):
        """
            This function sets the log level of the default handler as well as
            that of the logger itself.
        """
        self.default_handler.setLevel(lvl)
        super().setLevel(lvl)
        logging.getLogger(self.name).setLevel(lvl)

def getLogger(name='root'):
    """
        This functions behaves the same way as the logging.getLogger function
        behaves. It always returns the logger instance associated to the
        name given as a parameter.
    """
    if name not in __loggers__:
        __loggers__[name] = Logger(name)

    return __loggers__[name]

def setDefaultFormat(fmt):
    """
        This function sets the default format for every ModuleLogger.
        This format is only taken into account at the time of creation of a
        ModuleLogger object, and must follow the format described by the
        logging module documentation
    """
    __format__ = fmt


