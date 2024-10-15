import logging
import functools
from datetime import datetime, timezone
from os.path import basename, abspath, dirname

PROJECT_ROOT_PATH = dirname(dirname(abspath(__file__)))

class CustomFormatter(logging.Formatter):
    white = "\x1b[m"
    italic_white = "\x1b[3m"
    underline_white = "\x1b[4m"

    muted = "\x1b[38;2;2;20;5m"
    debug = "\x1b[38;50;2;2;5m"
    black = "\x1b[30m"
    lightgrey = "\x1b[37m"
    grey = "\x1b[38;20m"
    midgrey = "\x1b[90m"

    gold = "\x1b[33m"
    yellow = "\x1b[93m"
    yellow2 = "\x1b[33;20m"
    yellow3 = "\x1b[33;1m"
    lightyellow = "\x1b[38;2;250;250;150m"

    green = "\x1b[32m"
    mintgreen = "\x1b[38;2;150;250;150m"
    lightgreen = "\x1b[92m"
    othergreen = "\x1b[32;1m"
    drabgreen = "\x1b[38;2;150;200;150m"

    skyblue = "\x1b[38;2;150;250;250m"
    iceblue = "\x1b[38;2;59;142;200m"
    blue = "\x1b[34m"
    magenta = "\x1b[35m"
    purple = "\x1b[38;2;150;150;250m"
    cyan = "\x1b[36m"

    lightblue = "\x1b[96m"
    lightcyan = "\x1b[96m"

    pink = "\x1b[95m"
    lightred = "\x1b[91m"
    red = "\x1b[31;20m"
    red2 = "\x1b[31m"
    bold_red = "\x1b[31;1m"

    table = "\x1b[37m"
    status = "\x1b[94m"
    debug = "\x1b[30;1m"
    reset = "\x1b[0m"

    base_format = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)"
    datefmt = "%d-%b-%y %H:%M:%S"

    FORMATS = {
        logging.DEBUG: debug + base_format + reset,
        logging.INFO: lightgreen + base_format + reset,
        logging.WARNING: red + base_format + reset,
        logging.ERROR: lightred + base_format + reset,
        logging.CRITICAL: bold_red + base_format + reset,
    }

    # Custom level colors
    custom_colors = {
        "STOPWATCH": pink,
        "PAIR": skyblue,
        "DEXRPC": iceblue,
        "SOURCED": blue,
        "QUERY": lightyellow,
        "REQUEST": gold,
        "LOOP": purple,
        "CALC": lightcyan,
        "MERGE": cyan,
        "CACHED": drabgreen,
        "SAVED": mintgreen,
        "UPDATED": lightgreen,
        "MUTED": muted,
    }

    def format(self, record):
        # Use standard format unless custom color is available
        log_fmt = self.FORMATS.get(record.levelno, self.debug + self.base_format + self.reset)
        if record.levelname in self.custom_colors:
            log_fmt = self.custom_colors[record.levelname] + self.base_format + self.reset

        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)


def add_logging_levels(levels):
    """Dynamically add custom logging levels."""
    for level_name, level_num in levels.items():
        addLoggingLevel(level_name, level_num)
        logger.setLevel(level_name)
    logger.setLevel("DEBUG")


def addLoggingLevel(levelName, levelNum, methodName=None):
    """Add a custom log level."""
    methodName = methodName or levelName.lower()
    if hasattr(logging, levelName) or hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError(f"{levelName} or {methodName} already defined")
    if levelName.lower() in ["info", "debug", "warning", "error"]:
        stacklevel = 1
    else:
        stacklevel = 2
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs, stacklevel=stacklevel)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs, stacklevel=stacklevel)

    logging.addLevelName(levelNum, levelName)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


def send_log(loglevel, msg):
    """Dynamically send logs to the appropriate logger."""
    log_method = getattr(logger, loglevel.lower(), None)
    if log_method:
        log_method(f"   {msg}")
    else:
        logger.debug(f"   {msg}")


class StopWatch:
    def __init__(self, start_time, trace, loglevel="debug", msg=""):
        self.start_time = start_time
        self.trace = trace
        self.loglevel = loglevel
        self.msg = msg or "<<< no msg provided >>>"
        self.get_stopwatch()

    def get_stopwatch(self):
        duration = int(datetime.now(timezone.utc).timestamp()) - int(self.start_time)
        lineno = self.trace["lineno"]
        filename = self.trace["file"]
        func = self.trace["function"]
        self.msg = f"{duration:>2} sec | {func:<20} | {self.msg:<80} | {basename(filename)}:{lineno}"
        send_log(self.loglevel, self.msg)


def get_trace(func):
    """Get trace information for the current function."""
    return {
        "function": func.__name__,
        "file": func.__code__.co_filename,
        "lineno": func.__code__.co_firstlineno,
        "vars": func.__code__.co_varnames,
    }


def timed(func):
    """Decorator to log the runtime of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = int(datetime.now(timezone.utc).timestamp())
        trace = get_trace(func)
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            StopWatch(start_time, trace, loglevel="error", msg=f"{type(e).__name__}: {e}")
            raise
        StopWatch(start_time, trace, loglevel="info", msg="Function completed")
        return result
    return wrapper


# Create a logger and set up custom levels
logger = logging.getLogger("defi-stats")
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)

# Dynamically add all custom levels
custom_levels = {
    "SOURCED": logging.DEBUG + 14,
    "SAVED": logging.DEBUG + 13,
    "CACHED": logging.DEBUG + 12,
    "PAIR": logging.DEBUG + 11,
    "MERGE": logging.DEBUG + 9,
    "UPDATED": logging.DEBUG + 8,
    "QUERY": logging.DEBUG + 7,
    "DEXRPC": logging.DEBUG + 6,
    "LOOP": logging.DEBUG + 5,
    "CALC": logging.DEBUG + 4,
    "MUTED": logging.DEBUG - 1,
    "REQUEST": logging.DEBUG + 2
}

add_logging_levels(custom_levels)


def show_palette():
    """Show a sample of all log levels with colors."""
    log_levels = ["info", "debug", "warning", "error", "critical", "updated", "merge", "saved", "calc", 
                  "dexrpc", "loop", "muted", "query", "request", "cached"]
    for level in log_levels:
        send_log(level, level)


if __name__ == "__main__":
    show_palette()
