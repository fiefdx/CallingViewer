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
import chardet

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
        data["projects"] = [v for v in projects.all().itervalues()]
        data["projects"].sort(lambda x,y : cmp(x['project_name'], y['project_name']))
        self.write(data)

class ProjectAjaxLeafHandler(BaseHandler):
    def post(self):
        query_str = self.get_argument("query", "[]").strip()
        query = json.loads(query_str)
        project_name = self.get_argument("project_name", "").strip()

        LOG.info("query: %s, project_name: %s", query, project_name)

        nodes = []
        tree = []
        projects = Projects()
        if project_name != "" and projects.get(project_name):
            project = Project()
            project.parse_dict(projects.get(project_name))
            for q_id in query:
                dirs, files = project.listdir(q_id)
                if dirs != [] or files != []:
                    tree.append({"id": q_id})
                for d in dirs:
                    nodes.append({"id": os.path.join(q_id, d["name"]), 
                                  "parent": q_id, 
                                  "text": d["name"].replace("<", "&lt;").replace(">", "&gt;"), 
                                  "type": "directory"})
                for f in files:
                    nodes.append({"id": os.path.join(q_id, f["name"]), 
                                  "parent": q_id, 
                                  "text": f["name"].replace("<", "&lt;").replace(">", "&gt;"), 
                                  "type": "file"})

        data = {}
        data["nodes"] = nodes
        data["tree"] = tree
        self.write(data)

class ViewHandler(BaseHandler):
    def get(self):
        q = self.get_argument("q", "").strip()

        LOG.info("q: %s", q)

        file_path, line_num = "Can't read this file!", 0

        code = ""
        if os.path.exists(q) and os.path.isfile(q):
            with open(q, "rb") as fp:
                line = fp.readline()
                while line != "":
                    code += line
                    line = fp.readline()
                file_path = q

        data = {}
        data["code"] = ""
        encoding = chardet.detect(code)
        LOG.info("code encoding: %s", encoding)
        try:
            data["code"] = code.decode()
        except Exception, e:
            LOG.exception(e)
            try:
                data["code"] = code.decode("utf-8")
            except Exception, e:
                LOG.exception(e)
                try:
                    data["code"] = code.decode("gbk")
                except Exception, e:
                    LOG.exception(e)
                    try:
                        data["code"] = code.decode(encoding["encoding"])
                    except Exception, e:
                        LOG.exception(e)
                        file_path = "Can't read this file!"
        data["line"] = int(line_num)
        data["path"] = file_path
        file_name = "%s:%s" % (os.path.split(file_path)[-1], line_num)
        self.render("call/view.html", current_nav = "View", file_name = file_name, result = json.dumps(data))