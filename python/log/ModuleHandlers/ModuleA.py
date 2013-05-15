#!/usr/bin/env python3

import logging

def test():
    logger = logging.getLogger()
    logger.debug("This should not appear.")
    logger.info("This should appear.")
    logger.warn("This should appear.")
    logger.error("This should appear.")
    logger.critical("This should appear.")
