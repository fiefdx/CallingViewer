# -*- coding: utf-8 -*-
'''
Created on 2016-08-01
@summary: project
@author: YangHaitao
'''

import os
import logging
import json
import shutil

from config import CONFIG
from utils.common_utils import sha1sum, listdir

LOG = logging.getLogger(__name__)

class Project(object):
    def __init__(self):
        self.clear()

    def parse_dict(self, source):
        result = False
        self.clear()
        attrs = ["go_path", "main_path", "project_path", "project_name", "sha1"]
        if hasattr(source, "__getitem__"):
            for attr in attrs:
                try:
                    setattr(self, attr, source[attr])
                except:
                    LOG.debug("some exception occured when extract %s attribute to Project object, i will discard it", attr)
                    continue
            result = True
        else:
            LOG.debug("input param source does not have dict-like method, so i will do nothing at all!")
            result = False
        return result

    def to_dict(self):
        return {"go_path": self.go_path,
                "main_path": self.main_path,
                "project_path": self.project_path,
                "project_name": self.project_name,
                "sha1": self.sha1}

    def hash(self):
        self.sha1 = sha1sum(self.project_path.decode())

    def listdir(self, path = ""):
        dirs = []
        files = []
        try:
            if path == "":
                dirs, files = listdir(self.project_path)
            elif os.path.exists(path) and os.path.isdir(path):
                dirs, files = listdir(path)
        except Exception, e:
            LOG.exception(e)
        return dirs, files

    def clear(self):
        self.go_path = ""
        self.main_path = ""
        self.project_path = ""
        self.project_name = ""
        self.sha1 = ""

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
            project_data_path = os.path.join(CONFIG["data_path"], "projects", project.project_name)
            if not os.path.exists(project_data_path) or not os.path.isdir(project_data_path):
                os.makedirs(project_data_path)
            result = True
        except Exception, e:
            LOG.exception(e)
        return result

    def edit(self, project):
        self.__init()
        result = False
        try:
            if Projects.PROJECTS.has_key(project.project_name):
                Projects.PROJECTS[project.project_name] = project.to_dict()
                with open(self.config_path, "wb") as fp:
                    fp.write(json.dumps(Projects.PROJECTS))
            project_data_path = os.path.join(CONFIG["data_path"], "projects", project.project_name)
            if not os.path.exists(project_data_path) or not os.path.isdir(project_data_path):
                os.makedirs(project_data_path)
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
            project_data_path = os.path.join(CONFIG["data_path"], "projects", project_name)
            if os.path.exists(project_data_path) and os.path.isdir(project_data_path):
                shutil.rmtree(project_data_path)
            result = True
        except Exception, e:
            LOG.exception(e)
        return result

    def all(self):
        self.__init()
        with open(self.config_path, "rb") as fp:
            Projects.PROJECTS = json.loads(fp.read())
        return Projects.PROJECTS
