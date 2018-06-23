# -*- coding: utf-8 -*-
'''
Created on 2018-06-19
@summary: listdir
@author: YangHaitao
'''

import os
import logging
import json
import base64
import urllib

from config import CONFIG
from base import BaseHandler
from utils.common_utils import listdir_with_partitions

LOG = logging.getLogger(__name__)

class ListDirHandler(BaseHandler):
    def get(self):
        data = {}
        try:
            LOG.debug("arguments: %s", self.request.query_arguments)
            p = self.get_query_argument("p", "").strip()
            p = urllib.unquote(p)
            if not isinstance(p, unicode):
                p = p.decode("utf-8");
            LOG.debug("ListDirHandler, p: %s, %s", p, type(p))
            data = listdir_with_partitions(p)
            self.set_header('Content-Type', 'application/json; charset=utf-8')
        except Exception, e:
            LOG.exception(e)
            data["exception"] = "%s" % e
        self.write(json.dumps(data))
