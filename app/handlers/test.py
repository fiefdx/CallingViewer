# -*- coding: utf-8 -*-
'''
Created on 2014-05-28
@summary: test handler
@author: YangHaitao
'''

import os.path
import logging
import tornado

from config import CONFIG
from base import BaseHandler, BaseSocketHandler

LOG = logging.getLogger(__name__)

class TestHandler(BaseHandler):
    def get(self):
        self.write("This is a Test GET Page!")
