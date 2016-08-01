# -*- coding: utf-8 -*-
'''
Created on 2015-01-07
@summary: Storage sqlite interface
@author: YangHaitao
'''
import os
import logging
import sqlite3
import datetime
import time

from config import CONFIG

LOG = logging.getLogger(__name__)