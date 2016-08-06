# -*- coding: utf-8 -*-
'''
Created on 2015-09-18
@summary:  AISim yaml configuration
@author: YangHaitao
''' 
try:
    import yaml
except ImportError:
    raise ImportError("Config module requires pyYAML package, please check if pyYAML is installed!")

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import os
#
# default config
CONFIG = {}
try:
    # script in the app dir
    cwd = os.path.split(os.path.realpath(__file__))[0]
    configpath = os.path.join(cwd, "configuration.yml")
    localConf = load(stream = file(configpath), Loader = Loader)
    CONFIG.update(localConf)
    CONFIG["app_path"] = cwd
    CONFIG["pid_path"] = cwd
    CONFIG["config_path"] = cwd
    if not CONFIG.has_key("data_path"):
        CONFIG["data_path"] = os.path.join(os.path.split(cwd)[0], "DATA")
    datapath = CONFIG["data_path"]
    if not CONFIG.has_key("db_type"):
        CONFIG["db_type"] = "leveldb"
    if not CONFIG.has_key("process_num"):
        CONFIG["process_num"] = 1
    if not CONFIG.has_key("abs_path"):
        CONFIG["abs_path"] = ""
    if not CONFIG.has_key("max_recursion"):
        CONFIG["max_recursion"] = 30
    if not CONFIG.has_key("go_path"):
        CONFIG["go_path"] = ""
    with open(os.path.join(cwd, "Version"), "rb") as version_fp:
        CONFIG["version"] = version_fp.read().strip()

except Exception, e:
    print e

if __name__ == "__main__":
    print "cwd: %s"%cwd
    print "configpath: %s"%configpath
    print "CONFIG: %s"%CONFIG



