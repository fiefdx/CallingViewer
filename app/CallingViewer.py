# -*- coding: utf-8 -*-
'''
Created on 2015-09-18
@summary: main application entrance
@author: YangHaitao
'''

import os
import os.path
import signal
import logging
import socket
import time

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.locale
import tornado.netutil
import tornado.autoreload
from tornado.options import define, options

from app import Application
from utils import common
from utils.index_whoosh import IX
from config import CONFIG
import logger

cwd = os.path.split(os.path.realpath(__file__))[0]

define("host", default = CONFIG["server_host"], help = "run bind the given host", type = str)
define("port", default = CONFIG["server_port"], help = "run on the given port", type = int)
define("log", default = "Server.log", help = "specify the log file", type = str)

LOG = logging.getLogger(__name__)


if __name__ == "__main__":
    pid_path = os.path.join(CONFIG["pid_path"], "application.pid")
    PID = str(os.getpid())
    fp = open(pid_path, "wb")
    fp.write(PID)
    fp.close()
    os.environ["GOPATH"] = "%s%s" % (os.environ["GOPATH"] + ":" if os.environ.has_key("GOPATH") else "", CONFIG["go_path"])
    tornado.options.parse_command_line()
    logger.config_logging(file_name = options.log, 
                          log_level = CONFIG["log_level"], 
                          dir_name = "logs", 
                          day_rotate = False, 
                          when = "D", 
                          interval = 1, 
                          max_size = 20, 
                          backup_count = 5, 
                          console = True)
    http_server = tornado.httpserver.HTTPServer(Application(), no_keep_alive = False)
    common.Servers.HTTP_SERVER = http_server
    _ = IX(init_object = False)
    common.Servers.IX_SERVER = IX
    if CONFIG["app_debug"] == True:
        http_server.listen(options.port)
        LOG.info("Listen: localhost:%s", options.port)
    else:
        http_server.bind(options.port, address = options.host)
        http_server.bind(options.port, address = "127.0.0.1")
        http_server.start(num_processes = 1)
    try:
        signal.signal(signal.SIGTERM, common.sig_handler)
        signal.signal(signal.SIGINT, common.sig_handler)
        tornado.ioloop.IOLoop.instance().start()
    except Exception, e:
        LOG.exception(e)
    finally:
        if os.path.exists(pid_path) and os.path.isfile(pid_path):
            os.remove(pid_path)
            LOG.info("remove: [%s]", pid_path)
        LOG.info("Server Exit!")
