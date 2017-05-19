# -*- coding: utf-8 -*-
'''
Created on 2016-08-02
@summary: project handler
@author: YangHaitao
'''

import os
import logging
import json

from tornado import gen
import chardet

from config import CONFIG
from base import BaseHandler
from utils.index_whoosh import IX
from utils.async_project_import import MultiProcessProjectImport as ProjectImport
from utils.common_utils import get_mode
from utils import errors
from models.project import Project, Projects

LOG = logging.getLogger(__name__)

SEARCH_IX = IX()

def validate_params(project_name, project_path, go_path, main_path):
    try:
        if project_name.strip() == "":
            LOG.debug("validate params invalid project name: %s", project_name)
            return False
        if not os.path.exists(project_path) or not os.path.isdir(project_path):
            LOG.debug("validate params invalid project path: %s", project_path)
            return False
        go_paths = go_path.split(":")
        for p in go_paths:
            if not os.path.exists(p) or not os.path.isdir(p):
                LOG.debug("validate params invalid go path: %s", p)
                return False
        if not os.path.exists(main_path) or not os.path.isfile(main_path):
            LOG.debug("validate params invalid main path: %s", main_path)
            return False
    except Exception, e:
        LOG.exception(e)
        return False
    return True

class ProjectAjaxAddHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        data = {}
        try:
            project_name = self.get_argument("project_name", "").strip()
            project_path = self.get_argument("project_path", "").strip()
            project_path = project_path.rstrip("/") if project_path != "/" else "/"
            go_path = self.get_argument("go_path", "").strip()
            go_path = go_path.rstrip("/") if go_path != "/" else "/"
            main_path = self.get_argument("main_path", "").strip()

            LOG.debug("add project: project_name %s, project_path: %s, go_path: %s, main_path: %s", project_name, project_path, go_path, main_path)

            if not validate_params(project_name, project_path, go_path, main_path):
                raise errors.InvalidParamsError

            data["nodes"] = []
            data["tree"] = []
            data["project"] = ""
            projects = Projects()
            if project_name != "" and projects.exist(project_name):
                raise errors.ExistProjectError
            elif project_name != "" and not projects.exist(project_name) and os.path.exists(project_path) and os.path.isdir(project_path) and os.path.exists(main_path) and os.path.isfile(main_path):
                project = Project()
                project.go_path = go_path
                project.main_path = main_path
                project.project_path = project_path
                project.project_name = project_name
                project.hash()
                flag = projects.add(project)
                data["projects"] = [v for v in projects.all().itervalues()]
                data["projects"].sort(lambda x,y : cmp(x['project_name'], y['project_name']))
                if flag:
                    project_import = ProjectImport(CONFIG["process_num"])
                    data["project"] = project_name
                    nodes = []
                    project = Project()
                    project.parse_dict(projects.get(project_name))
                    project.hash()
                    data["project_path"] = project.project_path
                    data["main_path"] = project.main_path
                    data["go_path"] = project.go_path
                    SEARCH_IX.delete(project_name)
                    flag = SEARCH_IX.add(project_name)
                    if flag:
                        flag = yield project_import.import_project(project)
                        if flag:
                            LOG.info("Add Project[%s] Success", project_name)
                        else:
                            LOG.info("Add Project[%s] Failed", project_name)
                            flag = projects.delete(project.project_name)
                            if flag:
                                LOG.info("Delete Project[%s] (by add project failed) Success", project_name)
                            else:
                                LOG.error("Delete Project[%s] (by add project failed) Failed", project_name)
                            raise errors.AddProjectError
                        dirs, files = project.listdir()
                        if dirs != [] or files != []:
                            parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "directory"}
                        else:
                            parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "file"}
                        for d in dirs:
                            nodes.append({"id": os.path.join(project.project_path, d["name"]),
                                          "parent": project.project_path,
                                          "text": d["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                          "type": "directory"})
                        for f in files:
                            nodes.append({"id": os.path.join(project.project_path, f["name"]),
                                          "parent": project.project_path,
                                          "text": f["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                          "type": "file"})
                        nodes.insert(0, parent)
                        data["nodes"] = nodes
                elif len(data["projects"]) > 0:
                    nodes = []
                    data["project"] = data["projects"][0]["project_name"]
                    project = Project()
                    project.parse_dict(data["projects"][0])
                    data["project_path"] = project.project_path
                    data["main_path"] = project.main_path
                    data["go_path"] = project.go_path
                    dirs, files = project.listdir()
                    if dirs != [] or files != []:
                        parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "directory"}
                    else:
                        parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "file"}
                    for d in dirs:
                        nodes.append({"id": os.path.join(project.project_path, d["name"]),
                                      "parent": project.project_path,
                                      "text": d["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                      "type": "directory"})
                    for f in files:
                        nodes.append({"id": os.path.join(project.project_path, f["name"]),
                                      "parent": project.project_path,
                                      "text": f["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                      "type": "file"})
                    nodes.insert(0, parent)
                    data["nodes"] = nodes
            else:
                data["projects"] = [v for v in projects.all().itervalues()]
                data["projects"].sort(lambda x,y : cmp(x['project_name'], y['project_name']))
                nodes = []
                data["project"] = data["projects"][0]["project_name"]
                project = Project()
                project.parse_dict(data["projects"][0])
                data["project_path"] = project.project_path
                data["main_path"] = project.main_path
                data["go_path"] = project.go_path
                dirs, files = project.listdir()
                if dirs != [] or files != []:
                    parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "directory"}
                else:
                    parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "file"}
                for d in dirs:
                    nodes.append({"id": os.path.join(project.project_path, d["name"]),
                                  "parent": project.project_path,
                                  "text": d["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                  "type": "directory"})
                for f in files:
                    nodes.append({"id": os.path.join(project.project_path, f["name"]),
                                  "parent": project.project_path,
                                  "text": f["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                  "type": "file"})
                nodes.insert(0, parent)
                data["nodes"] = nodes
        except Exception, e:
            LOG.exception(e)
            data["exception"] = "%s" % e
        self.write(data)

class ProjectAjaxReindexHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        data = {}
        try:
            project_name = self.get_argument("project_name", "").strip()

            LOG.debug("reindex project: project_name %s", project_name)

            data["project"] = project_name
            projects = Projects()
            if project_name != "":
                project_import = ProjectImport(CONFIG["process_num"])
                project = Project()
                project.parse_dict(projects.get(project_name))
                project.hash()
                SEARCH_IX.delete(project_name)
                flag = SEARCH_IX.add(project_name)
                if flag:
                    flag = yield project_import.import_project(project)
                    if flag:
                        LOG.info("Reindex Project[%s] Success", project_name)
                    else:
                        LOG.info("Reindex Project[%s] Failed", project_name)
                        raise errors.ReindexProjectError
        except Exception, e:
            LOG.exception(e)
            data["exception"] = "%s" % e

        self.write(data)

class ProjectAjaxLeafHandler(BaseHandler):
    def post(self):
        query_str = self.get_argument("query", "[]").strip()
        query = json.loads(query_str)
        project_name = self.get_argument("project_name", "").strip()

        LOG.debug("query: %s, project_name: %s", query, project_name)

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

class ProjectAjaxSelectHandler(BaseHandler):
    def post(self):
        project_name = self.get_argument("project_name", "").strip()
        LOG.debug("project_name: %s", project_name)

        projects = Projects()
        data = {}
        data["nodes"] = []
        data["tree"] = []
        data["project"] = project_name
        nodes = []
        project = Project()
        project.parse_dict(projects.get(project_name))
        data["project_path"] = project.project_path
        data["main_path"] = project.main_path
        data["go_path"] = project.go_path
        dirs, files = project.listdir()
        if dirs != [] or files != []:
            parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "directory"}
        else:
            parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "file"}
        for d in dirs:
            nodes.append({"id": os.path.join(project.project_path, d["name"]),
                          "parent": project.project_path,
                          "text": d["name"].replace("<", "&lt;").replace(">", "&gt;"),
                          "type": "directory"})
        for f in files:
            nodes.append({"id": os.path.join(project.project_path, f["name"]),
                          "parent": project.project_path,
                          "text": f["name"].replace("<", "&lt;").replace(">", "&gt;"),
                          "type": "file"})
        nodes.insert(0, parent)
        data["nodes"] = nodes
        self.write(data)

class ProjectAjaxEditHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        data = {}
        try:
            project_name = self.get_argument("project_name", "").strip()
            project_path = self.get_argument("project_path", "").strip()
            project_path = project_path.rstrip("/") if project_path != "/" else "/"
            go_path = self.get_argument("go_path", "").strip()
            go_path = go_path.rstrip("/") if go_path != "/" else "/"
            main_path = self.get_argument("main_path", "").strip()

            LOG.debug("edit project: project_name %s, project_path: %s, go_path: %s, main_path: %s", project_name, project_path, go_path, main_path)

            if not validate_params(project_name, project_path, go_path, main_path):
                raise errors.InvalidParamsError

            data["nodes"] = []
            data["tree"] = []
            data["project"] = ""
            projects = Projects()
            if project_name != "" and os.path.exists(project_path) and os.path.isdir(project_path) and os.path.exists(main_path) and os.path.isfile(main_path):
                project = Project()
                project.go_path = go_path
                project.main_path = main_path
                project.project_path = project_path
                project.project_name = project_name
                project.hash()
                flag = projects.edit(project)
                data["projects"] = [v for v in projects.all().itervalues()]
                data["projects"].sort(lambda x,y : cmp(x['project_name'], y['project_name']))
                if flag:
                    project_import = ProjectImport(CONFIG["process_num"])
                    data["project"] = project_name
                    nodes = []
                    project = Project()
                    project.parse_dict(projects.get(project_name))
                    project.hash()
                    data["project_path"] = project.project_path
                    data["main_path"] = project.main_path
                    data["go_path"] = project.go_path
                    SEARCH_IX.delete(project_name)
                    flag = SEARCH_IX.add(project_name)
                    if flag:
                        flag = yield project_import.import_project(project)
                        if flag:
                            LOG.info("Edit Project[%s] Success", project_name)
                        else:
                            LOG.info("Edit Project[%s] Failed", project_name)
                            raise errors.EditProjectError
                        dirs, files = project.listdir()
                        if dirs != [] or files != []:
                            parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "directory"}
                        else:
                            parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "file"}
                        for d in dirs:
                            nodes.append({"id": os.path.join(project.project_path, d["name"]),
                                          "parent": project.project_path,
                                          "text": d["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                          "type": "directory"})
                        for f in files:
                            nodes.append({"id": os.path.join(project.project_path, f["name"]),
                                          "parent": project.project_path,
                                          "text": f["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                          "type": "file"})
                        nodes.insert(0, parent)
                        data["nodes"] = nodes
                elif len(data["projects"]) > 0:
                    nodes = []
                    data["project"] = data["projects"][0]["project_name"]
                    project = Project()
                    project.parse_dict(data["projects"][0])
                    data["project_path"] = project.project_path
                    data["main_path"] = project.main_path
                    data["go_path"] = project.go_path
                    dirs, files = project.listdir()
                    if dirs != [] or files != []:
                        parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "directory"}
                    else:
                        parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "file"}
                    for d in dirs:
                        nodes.append({"id": os.path.join(project.project_path, d["name"]),
                                      "parent": project.project_path,
                                      "text": d["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                      "type": "directory"})
                    for f in files:
                        nodes.append({"id": os.path.join(project.project_path, f["name"]),
                                      "parent": project.project_path,
                                      "text": f["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                      "type": "file"})
                    nodes.insert(0, parent)
                    data["nodes"] = nodes
            else:
                data["projects"] = [v for v in projects.all().itervalues()]
                data["projects"].sort(lambda x,y : cmp(x['project_name'], y['project_name']))
                nodes = []
                data["project"] = data["projects"][0]["project_name"]
                project = Project()
                project.parse_dict(data["projects"][0])
                data["project_path"] = project.project_path
                data["main_path"] = project.main_path
                data["go_path"] = project.go_path
                dirs, files = project.listdir()
                if dirs != [] or files != []:
                    parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "directory"}
                else:
                    parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "file"}
                for d in dirs:
                    nodes.append({"id": os.path.join(project.project_path, d["name"]),
                                  "parent": project.project_path,
                                  "text": d["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                  "type": "directory"})
                for f in files:
                    nodes.append({"id": os.path.join(project.project_path, f["name"]),
                                  "parent": project.project_path,
                                  "text": f["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                  "type": "file"})
                nodes.insert(0, parent)
                data["nodes"] = nodes
        except Exception, e:
            LOG.exception(e)
            data["exception"] = "%s" % e

        self.write(data)

class ProjectAjaxDeleteHandler(BaseHandler):
    def post(self):
        data = {}
        try:
            project_name = self.get_argument("project_name", "").strip()
            LOG.debug("project_name: %s", project_name)

            projects = Projects()
            data["nodes"] = []
            data["tree"] = []
            data["project"] = ""
            projects.delete(project_name)
            data["projects"] = [v for v in projects.all().itervalues()]
            data["projects"].sort(lambda x,y : cmp(x['project_name'], y['project_name']))
            if len(data["projects"]) > 0:
                nodes = []
                data["project"] = data["projects"][0]["project_name"]
                project = Project()
                project.parse_dict(data["projects"][0])
                data["project_path"] = project.project_path
                data["main_path"] = project.main_path
                data["go_path"] = project.go_path
                dirs, files = project.listdir()
                if dirs != [] or files != []:
                    parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "directory"}
                else:
                    parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "file"}
                for d in dirs:
                    nodes.append({"id": os.path.join(project.project_path, d["name"]),
                                  "parent": project.project_path,
                                  "text": d["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                  "type": "directory"})
                for f in files:
                    nodes.append({"id": os.path.join(project.project_path, f["name"]),
                                  "parent": project.project_path,
                                  "text": f["name"].replace("<", "&lt;").replace(">", "&gt;"),
                                  "type": "file"})
                nodes.insert(0, parent)
                data["nodes"] = nodes
        except Exception, e:
            LOG.exception(e)
            data["exception"] = "%s" % e
        self.write(data)

class ViewHandler(BaseHandler):
    def get(self):
        q = self.get_argument("q", "").strip()
        project_name = self.get_argument("p", "").strip()

        LOG.debug("q: %s", q)

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
        LOG.debug("code encoding: %s", encoding)
        try:
            data["code"] = code.decode()
        except Exception, e:
            try:
                data["code"] = code.decode("utf-8")
            except Exception, e:
                try:
                    data["code"] = code.decode("gbk")
                except Exception, e:
                    try:
                        data["code"] = code.decode(encoding["encoding"])
                    except Exception, e:
                        LOG.exception(e)
                        file_path = "Can't read this file!"
        data["ext"] = os.path.splitext(file_path)[-1].lower()
        data["line"] = int(line_num)
        data["path"] = file_path
        data["project"] = project_name
        file_name = "%s:%s" % (os.path.split(file_path)[-1], line_num)
        self.render("call/view.html", current_nav = "View", file_name = file_name, mode = get_mode(data["ext"]), result = json.dumps(data))
