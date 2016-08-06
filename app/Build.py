# -*- coding: utf-8 -*-
'''
Created on 2016-06-24
@summary: Analyse Calling Graph
@author: YangHaitao
'''

import sys
import os
import getopt
import logging
import datetime
import time
import shutil

from config import CONFIG
from utils.finder import Finder
from utils import common_utils
from utils.index_whoosh import IX, index_all_func
import logger

LOG = logging.getLogger(__name__)
INF = logging.getLogger("info")
INF.propagate = False

if __name__ == "__main__":
    logger.config_logging(
        file_name = "Build.log", 
        log_level = CONFIG["log_level"], 
        dir_name = "logs", 
        day_rotate = False, 
        when = "D", 
        interval = 1, 
        max_size = 50, 
        backup_count = 5, 
        console = True
    )
    logger.config_logging(
        logger_name = "info",
        file_name = "Info.log", 
        log_level = "NOSET", 
        dir_name = "logs", 
        day_rotate = False, 
        when = "D", 
        interval = 1, 
        max_size = 20, 
        backup_count = 10, 
        console = True
    )
    LOG.info("Start Build")
    os.environ["GOPATH"] = "%s%s" % (os.environ["GOPATH"] + ":" if os.environ.has_key("GOPATH") else "", CONFIG["go_path"])
    start_time = time.time()

    main_path = CONFIG["main_path"]
    data_path = os.path.join(CONFIG["data_path"], "data.callgraph")
    flag = common_utils.make_callgraph_data(main_path, data_path)
    if flag == True:
        db_path = os.path.join(CONFIG["data_path"], "table_calling.db")
        if os.path.exists(db_path) and os.path.isdir(db_path):
            shutil.rmtree(db_path)
            LOG.info("delete: %s", db_path)
        elif os.path.exists(db_path) and os.path.isfile(db_path):
            os.remove(db_path)
            LOG.info("delete: %s", db_path)
        db_path = os.path.join(CONFIG["data_path"], "table_called.db")
        if os.path.exists(db_path) and os.path.isdir(db_path):
            shutil.rmtree(db_path)
            LOG.info("delete: %s", db_path)
        elif os.path.exists(db_path) and os.path.isfile(db_path):
            os.remove(db_path)
            LOG.info("delete: %s", db_path)
        ix_path = os.path.join(CONFIG["data_path"], "index")
        if os.path.exists(ix_path) and os.path.isdir(ix_path):
            shutil.rmtree(ix_path)
            LOG.info("delete: %s", ix_path)
        finder = Finder(CONFIG["data_path"], called = True)
        finder.build_finder()
        ix = IX(init_object = True)
        index_all_func(db = finder.db, ix = ix)
        finder = Finder(CONFIG["data_path"], called = False)
        finder.build_finder()
        # ix = IX(init_object = True)
        index_all_func(db = finder.db, ix = ix)
    else:
        LOG.error("Create data.callgraph failed!")

    end_time = time.time()
    use_time = end_time - start_time
    LOG.info("End Build\nUse Time: %ss", use_time)
