# -*- coding: utf-8 -*-
'''
Created on 2016-08-01
@summary: project
@author: YangHaitao
'''

import sys
import os
import logging
import datetime
import time
import json

from config import CONFIG
from utils.common_utils import sha1sum

LOG = logging.getLogger(__name__)

class Project(object):
    def __init__(self):
        self.go_path = ""
        self.main_path = ""
        self.project_path = ""
        self.project_name = ""
        self.sha1 = ""

    def to_dict(self):
        return {"go_path": self.go_path,
                "main_path": self.main_path,
                "project_path": self.project_path,
                "project_name": self.project_name,
                "sha1": self.sha1}

    def hash(self):
        self.sha1 = sha1sum(self.project_path.decode())

class Projects(object):
    PROJECTS = None
    CONFIG_PATH = CONFIG["data_path"]

    def __init(self):
        self.config_path = os.path.join(Projects.CONFIG_PATH, "projects.conf")
        if Projects.PROJECTS == None:
            if os.path.exists(self.config_path) and os.path.isfile(self.config_path):
                with open(self.config_path, "rb") as fp:
                    Projects.PROJECTS = json.loads(fp.read())
            else:
                Projects.PROJECTS = {}
                with open(self.config_path, "wb") as fp:
                    fp.write(json.dumps(Projects.PROJECTS))

    def add(self, project):
        self.__init()
        result = False
        try:
            if not Projects.PROJECTS.has_key(project.project_name):
                Projects.PROJECTS[project.project_name] = project.to_dict()
                with open(self.config_path, "wb") as fp:
                    fp.write(json.dumps(Projects.PROJECTS))
            result = True
        except Exception, e:
            LOG.exception(e)
        return result

    def get(self, project_name):
        self.__init()
        result = False
        try:
            if Projects.PROJECTS.has_key(project_name):
                result = Projects.PROJECTS[project_name]
            else:
                result = None
        except Exception, e:
            LOG.exception(e)
        return result

    def delete(self, project_name):
        self.__init()
        result = False
        try:
            if Projects.PROJECTS.has_key(project_name):
                del(Projects.PROJECTS[project_name])
                with open(self.config_path, "wb") as fp:
                    fp.write(json.dumps(Projects.PROJECTS))
            result = True
        except Exception, e:
            LOG.exception(e)
        return result

    def all(self):
        self.__init()
        return Projects.PROJECTS

