#!/usr/bin/env python3

import ModuleLogger as logging
#import logging


logging.warn("test")

logger = logging.getLogger()
#logger = logging.getLogger("root")


logger.setLevel(logging.DEBUG)
logger.debug("debug msg")
logger.info("msg")
logger.warning("warn msg")

logger.setLevel(logging.WARNING)
logger.debug("debug msg")
logger.info("msg")
logger.warning("warn msg")

# ModuleLogger.Logger specific "easy call"
#logger.setFormat("%(message)s")

logger.debug("debug msg")
logger.info("msg")
logger.warning("warn msg")

#test of transparency between ModuleLogger and Logging
logging.getLogger("root").warn("warn root ?")
logging.warn("Critical error detected")

##
# Print out the logger dictionnary of the ModuleLogger
##
#print("")
#print("Printing key/objects...")
#print(str(logging.__loggers__))
#print("Printing done.")
