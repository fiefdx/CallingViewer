# -*- coding: utf-8 -*-
'''
Created on 2016-08-02
@summary: project handler
@author: YangHaitao
'''

import os
import logging
import json
import re

import tornado
from tornado import gen

from config import CONFIG
from base import BaseHandler, BaseSocketHandler
from utils.finder import Finder
from utils.index_whoosh import IX
from utils.project import Project, Projects

LOG = logging.getLogger(__name__)


class ProjectAjaxHandler(BaseHandler):
    def post(self):
        project_name = self.get_argument("project_name", "").strip()
        project_path = self.get_argument("project_path", "").strip()
        go_path = self.get_argument("go_path", "").strip()
        main_path = self.get_argument("main_path", "").strip()

        LOG.info("add project: project_name %s, project_path: %s, go_path: %s, main_path: %s", project_name, project_path, go_path, main_path)

        projects = Projects()
        flag = False
        if project_name != "" and os.path.exists(project_path) and os.path.isdir(project_path) and os.path.exists(main_path) and os.path.isfile(main_path):
            project = Project()
            project.go_path = go_path
            project.main_path = main_path
            project.project_path = project_path
            project.project_name = project_name
            project.hash()
            flag = projects.add(project)

        tree = []

        data = {}
        data["project"] = ""
        if flag == True:
            data["project"] = project_name
        data["nodes"] = []
        data["tree"] = []
        data["projects"] = [v for _, v in projects.all()]
        self.write(json.dumps(data))