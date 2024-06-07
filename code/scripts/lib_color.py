#!/usr/bin/env python3.12

from logger import logger

TODO: sunset this
def colorize(string, color):
    colors = {
        'black':'\033[30m',
        'error':'\033[31m',
        'red':'\033[31m',
        'green':'\033[32m',
        'orange':'\033[33m',
        'blue':'\033[34m',
        'purple':'\033[35m',
        'cyan':'\033[36m',
        'lightgrey':'\033[37m',
        'table':'\033[37m',
        'darkgrey':'\033[90m',
        'lightred':'\033[91m',
        'lightgreen':'\033[92m',
        'yellow':'\033[93m',
        'lightblue':'\033[94m',
        'status':'\033[94m',
        'pink':'\033[95m',
        'lightcyan':'\033[96m',
    }
    if color not in colors:
        return f"{string}"
    else:
        return f"{colors[color]} {string}\033[0m"


def color_input(msg):
  return input(colorize(msg, "orange"))

def table_logger.info(msg):
  logger.info(colorize(msg, "cyan"))

def info_logger.info(msg):
  logger.info(colorize(msg, "orange"))

def status_logger.info(msg):
  logger.info(colorize(msg, "status"))

def success_logger.info(msg):
  logger.info(colorize(msg, "green"))

def error_logger.info(msg):
  logger.info(colorize(msg, "error"))

def fade_logger.info(msg):
  logger.info(colorize(msg, "darkgrey"))

def wait_continue():
  color_input("Press [Enter] to continue...")
  