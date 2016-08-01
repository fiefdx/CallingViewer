# -*- coding: utf-8 -*-
'''
Created on 2015-01-07
@summary: Storage levelDB interface
@author: YangHaitao
'''
import os
import logging

import leveldb

from config import CONFIG
from db import sqlite_interface

LOG = logging.getLogger(__name__)


class FileStorage(object):
    DB_PATH = os.path.join(CONFIG["data_path"], "data_table")
    DB = None

    def __init__(self):
        FileStorage.DB_PATH = os.path.join(CONFIG["data_path"], "data_table")
        FileStorage.DB = leveldb.LevelDB(DB_PATH, block_size = 1024 * 1024 * 1024)

    @classmethod
    def get(cls, key):
        return cls.DB.Get(key)

    @classmethod
    def put(cls, key, value, sync = False):
        cls.DB.Put(key, value, sync)

    @classmethod
    def delete(cls, key, sync = False):
        cls.DB.Delete(key, sync)

    @classmethod
    def range_iter(cls, key_from = None, key_to = None, include_value = True):
        return cls.DB.RangeIter(key_from, key_to, include_value)

    @classmethod
    def get_stats(cls):
        return cls.DB.GetStats()

class FileStorage2(object):
    def __init__(self, db_name):
        self.db_path = os.path.join(CONFIG["data_path"], db_name)
        self.DB = leveldb.LevelDB(self.db_path, block_size = 1024 * 1024 * 1024)

    def get(self, key):
        return self.DB.Get(key)

    def put(self, key, value, sync = False):
        self.DB.Put(key, value, sync)

    def delete(self, key, sync = False):
        self.DB.Delete(key, sync)

    def range_iter(self, key_from = None, key_to = None, include_value = True):
        return self.DB.RangeIter(key_from, key_to, include_value)

    def get_stats(self):
        return self.DB.GetStats()