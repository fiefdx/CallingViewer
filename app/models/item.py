# -*- coding: utf-8 -*-
'''
Created on 2016-07-20
@summary: Item
@author: YangHaitao
'''

import os
import sys
import logging
import json
import datetime
import time

from utils.common_utils import sha1sum

LOG = logging.getLogger(__name__)

class FUNC(object):
    def __init__(self):
        self.clear()

    def __str__(self):
        string_formated = "id: %(id)d\n" \
                          "name: %(name)s\n" \
                          %(self.to_dict())
        return string_formated

    def parse_dict(self, source):
        '''
        @summary: parse the given dict to construct this FUNC object
        @param source: dict type input param
        @result: True/False
        '''
        result = False

        self.clear()
        attrs = ["id", "name"]
        if hasattr(source, "__getitem__"):
            for attr in attrs:
                try:
                    setattr(self, attr, source[attr])
                except:
                    LOG.debug("some exception occured when extract %s attribute to FUNC object, i will discard it",
                        attr)
                    continue
            result = True
        else:
            LOG.debug("input param source does not have dict-like method, so i will do nothing at all!")
            result = False
        return result

    def to_dict(self):
        """
        @summary: convert to a dict
        """
        return dict({
                "id" : self.id,
                "name" : self.name
                })

    def generate_id(self):
    	self.id = sha1sum(self.name.decode())
    	self.name = self.name.decode()

    def clear(self):
        """
        @summary: reset property:

        """
        self.id = ""
        self.name = ""