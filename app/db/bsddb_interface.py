# -*- coding: utf-8 -*-
'''
Created on 2016-06-30
@summary: Storage bsddb interface
@author: YangHaitao
'''
import os
import logging

import bsddb

from config import CONFIG
from db import sqlite_interface

LOG = logging.getLogger(__name__)


class FileStorage(object):
    DB_PATH = os.path.join(CONFIG["data_path"], "data_dsddb.db")
    DB = None

    def __init__(self):
        FileStorage.DB_PATH = os.path.join(CONFIG["data_path"], "data_dsddb.db")
        FileStorage.DB = bsddb.btopen(DB_PATH, "c")

    @classmethod
    def get(cls, key):
        return cls.DB[str(key)]

    @classmethod
    def put(cls, key, value, sync = False):
        cls.DB[str(key)] = value
        if sync:
            cls.DB.sync()

    @classmethod
    def delete(cls, key, sync = False):
        if cls.DB.has_key(str(key)):
            cls.DB.pop(str(key))
        if sync:
            cls.DB.sync()

class FileStorage2(object):
    def __init__(self, db_path, db_name):
        self.db_path = os.path.join(db_path, db_name)
        self.DB = bsddb.btopen(self.db_path, "c")

    def get(self, key):
        return self.DB[str(key)]

    def put(self, key, value, sync = False):
        self.DB[str(key)] = value
        if sync:
            self.DB.sync()

    def delete(self, key, sync = False):
        if self.DB.has_key(str(key)):
            self.DB.pop(str(key))
        if sync:
            self.DB.sync()

    def range_iter(self, key_from = None, key_to = None, include_value = True):
        if key_from != None and self.DB.has_key(str(key_from)):
            key, value = self.DB.set_location(key_from)
            if include_value:
                yield key, value
            else:
                yield key
        else:
            key, value = self.DB.first()
            if include_value:
                yield key, value
            else:
                yield key
        if key_to != None and self.DB.has_key(str(key_to)):
            end_key = key_to
        else:
            end_key, _ = self.DB.last()
        self.DB.first()
        while key != end_key:
            key, value = self.DB.next()
            if include_value:
                yield key, value
            else:
                yield key