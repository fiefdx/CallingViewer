# -*- coding: utf-8 -*-
'''
Created on 2016-07-26
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

from utils import common_utils
from config import CONFIG
import logger

LOG = logging.getLogger(__name__)


if __name__ == "__main__":
    os.environ["GOPATH"] = "%s" % "/home/breeze/Develop/IDGO"
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
    # common_utils.make_callgraph_data()
    r = common_utils.get_definition_from_guru("/home/breeze/Develop/IDGO/src/github.com/flike/idgo/server/command.go", 19, 15)
    LOG.debug("get_definition_from_guru: %s", r)
    tt = time.time()
    LOG.info("Use Time: %ss", tt - t)
    LOG.info("Test Exit!")
