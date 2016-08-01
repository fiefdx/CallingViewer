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

LOG = logging.getLogger(__name__)

class Project(object):
    def __init__(self):
        self.go_path = ""
        self.main_path = ""
        self.project_path = ""

    def to_dict(self):
        return {"go_path": self.go_path,
                "main_path": self.main_path,
                "project_path": self.project_path}

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
            if not Projects.PROJECTS.has_key(project.project_path):
                Projects.PROJECTS[project.project_path] = project.to_dict()
                with open(self.config_path, "wb") as fp:
                    fp.write(json.dumps(Projects.PROJECTS))
            result = True
        except Exception, e:
            LOG.exception(e)
        return result

    def get(self, project_path):
        self.__init()
        result = False
        try:
            if Projects.PROJECTS.has_key(project_path):
                result = Projects.PROJECTS[project_path]
            else:
                result = None
        except Exception, e:
            LOG.exception(e)
        return result

    def delete(self, project_path):
        self.__init()
        result = False
        try:
            if Projects.PROJECTS.has_key(project_path):
                del(Projects.PROJECTS[project_path])
                with open(self.config_path, "wb") as fp:
                    fp.write(json.dumps(Projects.PROJECTS))
            result = True
        except Exception, e:
            LOG.exception(e)
        return result

