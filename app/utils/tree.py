# -*- coding: utf-8 -*-
'''
Created on 2016-07-11
@summary: tree
@author: YangHaitao
'''

import sys
import os
import logging
import datetime
import time
import json
from copy import deepcopy

from operator import *
from tree_format import *

LOG = logging.getLogger(__name__)

def has_child(parent, key):
    for i, c in enumerate(parent):
        if c[0] == key:
            return i
    return -1

class Tree(object):
    def __init__(self):
        self.data = []

    def add(self, root = None, items = []):
        if root == None and len(items) > 0:
            index = has_child(self.data, items[0])
            if len(self.data) > 0 and index >= 0:
                self.add(self.data[index][1], items[1:])
            else:
                self.data.append([items[0], []])
                self.add(self.data[-1][1], items[1:])
            LOG.debug("add: %s", self.data)
        elif root != None and len(items) > 0:
            index = has_child(root, items[0])
            if len(root) > 0 and index >= 0:
                self.add(root[index][1], items[1:])
            else:
                root.append([items[0], []])
                self.add(root[-1][1], items[1:])
            LOG.debug("add: %s", self.data)

    def tree(self):
        result = []
        for d in self.data:
            d_tree = format_tree(d, format_node = itemgetter(0), get_children = itemgetter(1))
            result.append(d_tree)
        return "\n\n".join(result)


    def to_str(self):
        return str(self.data)

    def __str__(self):
        return str(self.to_str())

    def __repr__(self):
        return str(self.to_str())