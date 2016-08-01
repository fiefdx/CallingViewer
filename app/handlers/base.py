# -*- coding: utf-8 -*-
'''
Modified on 2014-10-29
@summary:  change get_current_user and get_current_user_key to return unicode
@author: YangHaitao
''' 

import logging
import os.path

import tornado.web
import tornado.locale
import tornado.websocket

LOG = logging.getLogger(__name__)

class BaseHandler(tornado.web.RequestHandler):
    pass

class BaseSocketHandler(tornado.websocket.WebSocketHandler):
    pass