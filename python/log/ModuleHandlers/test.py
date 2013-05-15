#!/usr/bin/env python3

"""
The level of the logging operation is tested in the logger's log() method.
Other conditions may be tested within the filters to reject a record.


In order, within a root logger to keep all records and filter them by
(module, level), the root logger must be set at the lowest level (DEBUG).

Then, two strategies are offered:
 - Use one unique filter containing all (module, level) associations.
 - Use one simple filter for each module, and add them all to the handler.
"""


import logging
import ModuleFilter

import ModuleA
import ModuleB
import ModuleC

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] <%(module)s> %(name)s: %(message)s")

handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

# Add filters for three test modules
handler.addFilter(ModuleFilter.Filter(ModuleA, logging.INFO))
handler.addFilter(ModuleFilter.Filter(ModuleB, logging.DEBUG))
handler.addFilter(ModuleFilter.Filter(ModuleC, logging.WARNING))

root_logger.addHandler(handler)


ModuleA.test()
ModuleB.test()
ModuleC.test()
