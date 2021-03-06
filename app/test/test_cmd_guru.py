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
    common_utils.check_guru()
    LOG.debug("check_guru: guru: %s", common_utils.GURU)
    tt = time.time()
    LOG.info("Use Time: %ss", tt - t)
    LOG.info("Test Exit!")
