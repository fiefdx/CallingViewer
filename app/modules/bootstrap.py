# -*- coding: utf-8 -*-
'''
Created on 2015-01-06
@summary:
@author: YangHaitao
'''

import tornado.web
import logging
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

class NeedJsLib(tornado.web.UIModule):
    def render(self, mode):
        mode_map = {"text/x-go": "go/go",
                    "text/x-php": "php/php",
                    "text/x-python": "python/python",
                    "text/x-cython": "python/python",
                    "text/x-java:": "clike/clike",
                    "text/x-c++src": "clike/clike",
                    "text/x-csrc": "clike/clike",
                    "text/x-scss": "css/css",
                    "text/x-sh": "shell/shell",
                    "text/javascript": "javascript/javascript",
                    "text/html": "htmlmixed/htmlmixed",
                    "application/json": "javascript/javascript",
                    "text/x-sql": "sql/sql",
                    "text/x-yaml": "yaml/yaml",
                    "text/x-toml": "toml/toml",
                    "text/x-markdown": "markdown/markdown",
                    "text/x-lua": "lua/lua"}
        format_str = '''<script src="/static/js/codemirror/mode/%s.js"></script>'''
        if mode in mode_map:
            return format_str % mode_map[mode]
        else:
            return ""
