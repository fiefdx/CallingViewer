# -*- coding: utf-8 -*-
'''
Created on 2015-01-06
@summary:
@author: YangHaitao
'''

import tornado.web
import logging
import math
import urlparse
import urllib
import re

from config import CONFIG

LOG = logging.getLogger(__name__)

class JsString(tornado.web.UIModule):
    '''
    @summary: create a javascript string

    '''
    def escape_string(self, string):
        return re.sub(r"([\"\'\\])", r"\\\1", string)

    def render(self, js_str):
        js_str = self.escape_string(js_str)
        return js_str.encode("utf-8")

