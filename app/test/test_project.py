# -*- coding: utf-8 -*-
'''
Created on 2016-08-01
@summary: test
@author: YangHaitao
'''

import os
import os.path
import logging
import time
import sys

cwd = os.path.split(os.path.realpath(__file__))[0]
sys.path.insert(0, os.path.split(cwd)[0])

from models.project import Project, Projects
from config import CONFIG
import logger

LOG = logging.getLogger(__name__)


if __name__ == "__main__":
    os.environ["GOPATH"] = "%s%s" % (os.environ["GOPATH"] + ":" if os.environ.has_key("GOPATH") else "", CONFIG["go_path"])
    logger.config_logging(file_name = "test.log",
                          log_level = CONFIG["log_level"],
                          dir_name = "logs",
                          day_rotate = False,
                          when = "D",
                          interval = 1,
                          max_size = 20,
                          backup_count = 5,
                          console = True)
    LOG.info("Test Start")
    t = time.time()
    p = Projects()
    p_1 = Project()
    p_1.go_path = "go_path"
    p_1.main_path = "main_path"
    p_1.project_path = "project_path"
    p_1.project_name = "project_name"
    p_1.hash()
    p.add(p_1)
    # p.delete("project_path")
    tt = time.time()
    LOG.info("Use Time: %ss", tt - t)
    LOG.info("Test Exit!")
