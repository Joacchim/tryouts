#!/usr/bin/env python3

import logging

class Filter(logging.Filter):
    """
        Since a filter can be a veto to all other filters,
        the filter should return a negative answer only if the log level
        does not match (and not reject records for other modules).
    """
    def __init__(self, module, level=logging.NOTSET):
        self.level = logging._checkLevel(level)
        self.module = module.__name__
        self.nlen = 0

    def filter(self, record):
        if record.module == self.module and self.level > record.levelno:
            return 0
        # By default, accept everything.
        return 1

