# -*- coding: utf-8 -*-
'''
Created on 2016-07-20
@summary:  some utils
@author: YangHaitao
''' 

import sys
import os
import re
import getopt
import logging
import shutil
import datetime
import time
import hashlib
import subprocess
from subprocess import Popen

from config import CONFIG

LOG = logging.getLogger(__name__)

def sha1sum(content):
    '''
    param content must be unicode
    result is unicode
    '''
    m = hashlib.sha1(content.encode("utf-8"))
    m.digest()
    result = m.hexdigest().decode("utf-8")
    return result

def sha256sum(content):
    '''
    param content must be unicode
    result is unicode
    '''
    m = hashlib.sha256(content.encode("utf-8"))
    m.digest()
    result = m.hexdigest().decode("utf-8")
    return result

def md5twice(content):
    '''
    param content must be unicode
    result is unicode
    '''
    m = hashlib.md5(content.encode("utf-8")).hexdigest()
    result = hashlib.md5(m).hexdigest().decode("utf-8")
    return result

def make_callgraph_data():
    result = False
    cmd = r'callgraph -algo=cha -format="\"{{.Caller}}\" \"{{.Callee}}\" \"{{.Filename}}:{{.Line}}\"" %s > %s'
    main_path = CONFIG["main_path"]
    data_path = os.path.join(CONFIG["data_path"], "data.callgraph")
    LOG.debug("cmd: %s", cmd % (main_path, data_path))
    try:
        p = Popen(cmd % (main_path, data_path), shell = True)
        p.wait()
        result = True
    except Exception, e:
        LOG.exception(e)
    return result

