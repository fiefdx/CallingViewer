# -*- coding: utf-8 -*-
'''
Created on 2016-08-06
@summary: multi-process async import project
@author: YangHaitao
'''

import os
import sys
import shutil
import logging
import json
import time
import signal
import binascii
import dateutil
import hashlib
import datetime
import time
from time import localtime, strftime
from multiprocessing import Process, Pipe

import tornado
from tornado import gen
from tornado.ioloop import IOLoop
import toro

from config import CONFIG
from utils.finder import Finder
from utils import common_utils
from utils.project import Project, Projects
from utils.index_whoosh import IX, index_all_func
import logger

LOG = logging.getLogger(__name__)


def crc32sum_int(data, crc = None):
    '''
    data is string
    crc is a CRC32 int
    '''
    result = ""
    if crc == None:
        result = binascii.crc32(data)
    else:
        result = binascii.crc32(data, crc)
    return result

class ProjectImportProcess(Process):
    def __init__(self, process_id, pipe_client):
        Process.__init__(self)
        self.process_id = process_id
        self.pipe_client = pipe_client
        self.finder = None
        self.ix = None

    def run(self):
        date_time = strftime("%Y%m%d_%H%M%S", localtime())
        logger.config_logging(file_name = ("project_import_%s_" % self.process_id + '.log'), 
                              log_level = CONFIG['log_level'], 
                              dir_name = "logs", 
                              day_rotate = False, 
                              when = "D", 
                              interval = 1, 
                              max_size = 20, 
                              backup_count = 5, 
                              console = True)
        LOG.info("Start ProjectImportProcess(%s)", self.process_id)
        try:
            while True:
                try:
                    command, project = self.pipe_client.recv()
                    if command == "IMPORT":
                        LOG.debug("ProjectImportProcess import %s[%s] to Process(%s)", project.sha1, project.project_name, self.process_id)
                        # os.environ["GOPATH"] = "%s%s" % (os.environ["GOPATH"] + ":" if os.environ.has_key("GOPATH") else "", CONFIG["go_path"])
                        os.environ["GOPATH"] = project.go_path
                        LOG.info("GOPATH: %s", os.environ["GOPATH"])

                        data_path = os.path.join(CONFIG["data_path"], "projects", project.project_name)
                        flag = common_utils.make_callgraph_data(project.main_path, os.path.join(data_path, "data.callgraph"))
                        if flag == True:
                            LOG.debug("generate data.callgraph success")
                            db_path = os.path.join(data_path, "table_calling.db")
                            if os.path.exists(db_path) and os.path.isdir(db_path):
                                shutil.rmtree(db_path)
                                LOG.info("delete: %s", db_path)
                            elif os.path.exists(db_path) and os.path.isfile(db_path):
                                os.remove(db_path)
                                LOG.info("delete: %s", db_path)
                            db_path = os.path.join(data_path, "table_called.db")
                            if os.path.exists(db_path) and os.path.isdir(db_path):
                                shutil.rmtree(db_path)
                                LOG.info("delete: %s", db_path)
                            elif os.path.exists(db_path) and os.path.isfile(db_path):
                                os.remove(db_path)
                                LOG.info("delete: %s", db_path)
                            finder = Finder(data_path, called = True)
                            finder.build_finder()
                            projects = Projects()
                            ix = IX(projects = [v for v in projects.all().itervalues()])
                            LOG.debug("IX: %s", IX.IX_INDEXS)
                            index_all_func(db = finder.db, ix = ix.get(project.project_name))
                            finder = Finder(data_path, called = False)
                            finder.build_finder()
                            index_all_func(db = finder.db, ix = ix.get(project.project_name))
                        else:
                            LOG.error("Create data.callgraph failed!")
                        if flag == True:
                            self.pipe_client.send((command, True))
                        else:
                            self.pipe_client.send((command, False))
                    elif command == "EXIT":
                        LOG.info("ProjectImportProcess(%s) exit by EXIT command!", self.process_id)
                        return
                except EOFError:
                    LOG.error("EOFError ProjectImportProcess(%s) Write Thread exit!", self.process_id)
                    return
                except Exception, e:
                    LOG.exception(e)
            LOG.info("Leveldb Process(%s) exit!", self.process_id)
        except KeyboardInterrupt:
            LOG.info("KeyboardInterrupt: ProjectImportProcess(%s) exit!", self.process_id)
        except Exception, e:
            LOG.exception(e)

class MultiProcessProjectImport(object):
    PROCESS_LIST = []
    PROCESS_DICT = {}
    WRITE_LOCKS = []
    READ_LOCKS = []
    _instance = None

    def __init__(self, process_num = 1):
        if MultiProcessProjectImport._instance == None:
            self.process_num = process_num
            for i in xrange(process_num):
                pipe_master, pipe_client = Pipe()
                MultiProcessProjectImport.WRITE_LOCKS.append(toro.Lock())
                MultiProcessProjectImport.READ_LOCKS.append(toro.Lock())
                p = ProjectImportProcess(i, pipe_client)
                p.daemon = True
                MultiProcessProjectImport.PROCESS_LIST.append(p)
                MultiProcessProjectImport.PROCESS_DICT[i] = [p, pipe_master]
                p.start()
            MultiProcessProjectImport._instance = self
        else:
            self.process_num = MultiProcessProjectImport._instance.process_num

    @gen.coroutine
    def import_project(self, project):
        """
        project: a Project object
        """
        result = False
        process_id = crc32sum_int(project.project_name) % self.process_num
        # acquire write lock
        LOG.debug("Start import %s to Process(%s)", project.project_name, process_id)
        with (yield MultiProcessProjectImport.WRITE_LOCKS[process_id].acquire()):
            LOG.debug("Get import Lock %s to Process(%s)", project.project_name, process_id)
            MultiProcessProjectImport.PROCESS_DICT[process_id][1].send(("IMPORT", project))
            LOG.debug("Send import %s to Process(%s) end", project.project_name, process_id)
            while not MultiProcessProjectImport.PROCESS_DICT[process_id][1].poll():
                yield gen.moment
            LOG.debug("RECV import %s to Process(%s)", project.project_name, process_id)
            r = MultiProcessProjectImport.PROCESS_DICT[process_id][1].recv()
            LOG.debug("End import %s to Process(%s)", project.project_name, process_id)
        LOG.debug("ProjectImportProcess(%s): %s", process_id, r[1])
        if r[1]:
            result = r[1]
        raise gen.Return(result)

    @gen.coroutine
    def get_progress(self, project_name):
        result = False
        raise gen.Return(result)

    def close(self):
        try:
            for i in MultiProcessProjectImport.PROCESS_DICT.iterkeys():
                MultiProcessProjectImport.PROCESS_DICT[i][1].send(("EXIT", None))
            for i in MultiProcessProjectImport.PROCESS_DICT.iterkeys():
                while MultiProcessProjectImport.PROCESS_DICT[i][0].is_alive():
                    time.sleep(0.5)
            LOG.info("All ProjectImport Process Exit!")
        except Exception, e:
            LOG.exception(e)
