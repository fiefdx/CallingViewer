# -*- coding: utf-8 -*-
'''
Created on 2015-09-18
@summary: master common utilities
@author: YangHaitao
'''
import os
import time
import json
import logging

import tornado.ioloop
from tornado import gen

from config import CONFIG

LOG = logging.getLogger(__name__)
MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3

class Servers(object):
    HTTP_SERVER = None
    IX_SERVER = None
    PROJECT_SERVER = None

def is_browser(headers):
    result = False
    user_agent = None
    if headers.has_key("User-Agent"):
        user_agent = headers["User-Agent"].lower()
    LOG.debug("User-Agent: %s", user_agent)
    if user_agent and ("mozilla" in user_agent or "chromium" in user_agent 
       or "chrome" in user_agent or "safari" in user_agent):
        result = "browser"
    elif user_agent and ("curl" in user_agent):
        result = "curl"
    return result

def make_write_message(is_browser, info):
    result = ""
    # for browser
    if is_browser == "browser":
        result = json.dumps(info, indent = 4, sort_keys = True).replace("\n", "<br>").replace(" ", "&nbsp;").replace("\\n", "<br>")
    # for curl
    elif is_browser == "curl":
        result = json.dumps(info, indent = 4, sort_keys = True).replace("\\n", "\n") + "\n"
    # for other
    else:
        result = json.dumps(info, indent = 4, sort_keys = True) + "\n"
    return result

@gen.coroutine
def get_dir_size(source):
    total_size = os.path.getsize(source)
    n = 1
    for item in os.listdir(source):
        if n % 160 == 0:
            yield gen.moment
        itempath = os.path.join(source, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += yield get_dir_size(itempath)
        n += 1
    # return total_size
    raise gen.Return(total_size)

@gen.coroutine
def get_file_size_gb(file_path):
    result = False
    s = time.time()
    if os.path.exists(file_path) and os.path.isfile(file_path):
        result = int(os.path.getsize(file_path) / (1024*1024*1024))
    elif os.path.exists(file_path) and os.path.isdir(file_path):
        size = yield get_dir_size(file_path)
        result = int(size / (1024*1024*1024))
    LOG.debug("get file size: %s GB, use time: %ss", result, time.time() - s)
    raise gen.Return(result)


def shutdown():
    LOG.info("Stopping Server(%s:%s)", CONFIG["server_host"], 
                                       CONFIG["server_port"])
    if Servers.HTTP_SERVER:
        Servers.HTTP_SERVER.stop()
        LOG.info("Stop http server!")
    if Servers.IX_SERVER:
        Servers.IX_SERVER.cls_close()
        LOG.info("Stop ix server!")
    if Servers.PROJECT_SERVER:
        Servers.PROJECT_SERVER.close()
        LOG.info("Stop POSTER!")
    LOG.info("Will shutdown in %s seconds ...", MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
    io_loop = tornado.ioloop.IOLoop.instance()
    deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN
 
    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            LOG.info("Server(%s:%s) Shutdown!", CONFIG["server_host"], 
                                                CONFIG["server_port"])

    stop_loop()

def sig_handler(sig, frame):
    LOG.warning("Caught signal: %s", sig)
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)
