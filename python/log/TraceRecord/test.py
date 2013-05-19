#!/usr/bin/env python3

import logging

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter("[{levelname}] <{module}> {filename}:{lineno}: In file {src[file]} on line {src[line]} at col {src[col]}", style="{")

handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

root_logger.addHandler(handler)


# Test it out with simple formatting.
d = { 'src': {'line': 14, 'col': 45, 'file': "file.py"}, 'error': "success" }
print("In file {src[file]} on line {src[line]} at col {src[col]}: {error}".format(**d))


root_logger.info("", extra=d)
