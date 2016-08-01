# -*- coding: utf-8 -*-
'''
Created on 2014-05-07
@summary: A custom logging
@author: YangHaitao
'''

import os
import logging
import logging.handlers

CWD = os.path.split(os.path.realpath(__file__))[0]

LEVELS = {'NOSET': logging.NOTSET,
          'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARNING': logging.WARNING,
          'ERROR': logging.ERROR,
          'CRITICAL': logging.CRITICAL}

class ConsoleStreamHandler(logging.StreamHandler):
    # color names to indices
    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
    }
    # levels to (background, foreground, bold/intense)
    level_map = {
        logging.DEBUG: (None, 'blue', False),
        logging.INFO: (None, 'white', False),
        logging.WARNING: (None, 'yellow', False),
        logging.ERROR: (None, 'red', False),
        logging.CRITICAL: ('red', 'white', True),
    }

    csi = '\x1b['
    reset = '\x1b[0m'

    def colorize(self, message, record):
        """
        Colorize a message for a logging event.

        This implementation uses the ``level_map`` class attribute to
        map the LogRecord's level to a colour/intensity setting, which is
        then applied to the whole message.

        :param message: The message to colorize.
        :param record: The ``LogRecord`` for the message.
        """
        if record.levelno in self.level_map:
            bg, fg, bold = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))
            if bold:
                params.append('1')
            if params:
                message = ''.join((self.csi, ';'.join(params), 'm', message, self.reset))
        return message

    def format(self, record):
        """
        Formats a record for output.

        This implementation colorizes the message line, but leaves
        any traceback unolorized.
        """
        message = logging.StreamHandler.format(self, record)
        parts = message.split('\n', 1)
        parts[0] = self.colorize(parts[0], record)
        message = '\n'.join(parts)
        return message

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if unicode and isinstance(message, unicode):
                enc = getattr(stream, 'encoding', 'utf-8')
                message = message.encode(enc, 'replace')
            stream.write(message)
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def config_logging(logger_name = "",
                   file_name = "main.log", 
                   log_level = "NOSET", 
                   dir_name = "logs", 
                   day_rotate = False, 
                   when = "D", 
                   interval = 1, 
                   max_size = 50, 
                   backup_count = 5, 
                   console = True):
    format_log_string = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
    format_console_string = "%(name)-12s: %(levelname)-8s %(message)s"
    logs_dir = os.path.join(CWD, dir_name)
    file_dir = os.path.join(logs_dir, file_name)
    # init logs directory
    if os.path.exists(logs_dir) and os.path.isdir(logs_dir):
       pass
    else:
        os.makedirs(logs_dir)
    # clear all handlers
    logging.getLogger(logger_name).handlers = []
    # init rotating handler
    if day_rotate == True:
        rotatingFileHandler = logging.handlers.TimedRotatingFileHandler(filename = file_dir,
                                                                        when = when,
                                                                        interval = interval,
                                                                        backupCount = backup_count)
    else:
        rotatingFileHandler = logging.handlers.RotatingFileHandler(filename = file_dir,
                                                                   maxBytes = 1024 * 1024 * max_size,
                                                                   backupCount = backup_count)
    formatter = logging.Formatter(format_log_string)
    rotatingFileHandler.setFormatter(formatter)
    logging.getLogger(logger_name).addHandler(rotatingFileHandler)
    # add a console handler
    if console == True:
        if os.name == 'nt':
            consoleHandler = logging.StreamHandler()
        else:
            consoleHandler = ConsoleStreamHandler()
        # set console log level
        consoleHandler.setLevel(LEVELS[log_level.upper()])
        formatter = logging.Formatter(format_console_string)
        consoleHandler.setFormatter(formatter)
        logging.getLogger(logger_name).addHandler(consoleHandler)
    # set log level
    logger = logging.getLogger(logger_name)
    level = LEVELS[log_level.upper()]
    logger.setLevel(level)