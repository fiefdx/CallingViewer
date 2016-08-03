# -*- coding: utf-8 -*-
'''
Created on 2016-07-12
@summary: call handler
@author: YangHaitao
'''

import os.path
import logging
import json
import re

import tornado
from tornado import gen

from config import CONFIG
from base import BaseHandler, BaseSocketHandler
from utils.finder import Finder
from utils.search_whoosh import search_index_no_page
from utils.index_whoosh import IX
from utils.project import Project, Projects

LOG = logging.getLogger(__name__)

ID_SP = "____"

class CallHandler(BaseHandler):
    def get(self):
        projects = Projects()
        data = {}
        data["nodes"] = []
        data["tree"] = []
        data["projects"] = [v for v in projects.all().itervalues()]
        data["projects"].sort(lambda x,y : cmp(x['project_name'], y['project_name']))
        if len(data["projects"]) > 0:
            nodes = []
            data["project"] = data["projects"][0]["project_name"]
            project = Project()
            project.parse_dict(data["projects"][0])
            dirs, files = project.listdir()
            if dirs != [] or files != []:
                parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "tree"}
            else:
                parent = {"id": project.project_path, "parent": "#", "text": os.path.split(project.project_path)[-1], "type": "leaf"}
            for d in dirs:
                nodes.append({"id": os.path.join(project.project_path, d["name"]), 
                              "parent": project.project_path, 
                              "text": d["name"].replace("<", "&lt;").replace(">", "&gt;"), 
                              "type": "leaf"})
            for f in files:
                nodes.append({"id": os.path.join(project.project_path, f["name"]), 
                              "parent": project.project_path, 
                              "text": f["name"].replace("<", "&lt;").replace(">", "&gt;"), 
                              "type": "leaf"})
            nodes.insert(0, parent)
            data["nodes"] = nodes

        self.render("call/call_tree.html", current_nav = "View", version = CONFIG["version"], result = json.dumps(data))

    def post(self):
        query = self.get_argument("query", "").strip()
        called_str = self.get_argument("called", "false").strip()
        called = True if called_str == "true" else False
        filter_str = self.get_argument("filter", "").strip()
        LOG.info("query: %s, called: %s, filter: %s", query, called, filter_str)

        finder = Finder(CONFIG["data_path"], called = called)
        r = finder.find(query)

        r_filtered = []
        tree = []
        if r != None and r != False:
            if filter_str != "":
                for item in r:
                    if filter_str in item[0]:
                        r_filtered.append(item)
            else:
                r_filtered = r
        
            if r_filtered != []:
                parent = {"id": query, "parent": "#", "text": query, "type": "tree"}
            else:
                parent = {"id": query, "parent": "#", "text": query, "type": "leaf"}
            for item in r_filtered:
                if item[0] == query:
                    pass
                else:
                    tree.append({"id": "%s%s%s%s%s" % (query, ID_SP, item[0], ID_SP, item[1]), 
                                 "parent": query, 
                                 "text": item[0].replace("<", "&lt;").replace(">", "&gt;"), 
                                 "type": "leaf"})
        
            tree.sort(lambda x,y : cmp(x['text'], y['text']))
            tree.insert(0, parent)
        LOG.debug("tree: %s", tree)
        data = {}
        data["query"] = query
        data["tree"] = tree
        data["called"] = called
        data["filter"] = filter_str
        self.write(data)

class CallAjaxHandler(BaseHandler):
    def post(self):
        query_str = self.get_argument("query", "[]").strip()
        query = json.loads(query_str)
        called_str = self.get_argument("called", "false").strip()
        called = True if called_str == "true" else False
        filter_str = self.get_argument("filter", "").strip()
        LOG.info("query: %s, called: %s, filter: %s", query, called, filter_str)

        finder = Finder(CONFIG["data_path"], called = called)
        nodes = []
        tree = []
        for q_id in query:
            q = q_id.split(ID_SP)[1]
            r = finder.find(q)

            r_filtered = []
            if r != None and r != False:
                if filter_str != "":
                    for item in r:
                        if filter_str in item[0]:
                            r_filtered.append(item)
                else:
                    r_filtered = r

                if r_filtered != []:
                    tree.append({"id": q_id})
                for item in r_filtered:
                    if item[0] == q:
                        pass
                    else:
                        nodes.append({"id": "%s%s%s%s%s" % (q, ID_SP, item[0], ID_SP, item[1]), 
                                      "parent": q_id, 
                                      "text": item[0].replace("<", "&lt;").replace(">", "&gt;"), 
                                      "type": "leaf"})
        
        nodes.sort(lambda x,y : cmp(x['text'], y['text']))
        LOG.debug("tree: %s", tree)
        data = {}
        data["nodes"] = nodes
        data["tree"] = tree
        data["called"] = called
        data["filter"] = filter_str
        self.write(data)

class ViewHandler(BaseHandler):
    def get(self):
        q = self.get_argument("q", "").strip()
        d = self.get_argument("d", "false").strip() # definition
        d = True if d == "true" else False
        called_str = self.get_argument("called", "false").strip()
        called = True if called_str == "true" else False
        q_list = []
        if ID_SP in q:
            q_list = q.split(ID_SP)
        else:
            q_list = ["", q, ""]

        LOG.info("q: %s, d: %s, called: %s", q, d, called)

        file_path, line_num = "Can't open the root element's file!", 0

        code = ""
        if d == False:
            if q != "":
                q = q_list[-1]

            if q != "":
                if ":" in q:
                    file_path, line_num = q.split(":")

                if not os.path.isabs(file_path):
                    file_path = os.path.join(CONFIG["abs_path"], file_path)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    with open(file_path, "rb") as fp:
                        code = fp.read()
        elif d == True and "$" in q_list[1]:
            if ID_SP in q and ":" in q and called == False:
                q = q_list[-1]
                file_path, line_num = q.split(":")
                if not os.path.isabs(file_path):
                    file_path = os.path.join(CONFIG["abs_path"], file_path)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    with open(file_path, "rb") as fp:
                        code = fp.read()
            else:
                r = []
                q = q_list[1]
                finder = Finder(CONFIG["data_path"], called = True)
                r = finder.find(q)
                LOG.debug("r: %s", r)
                if r != [] and r != None and r != False:
                    file_path, line_num = r[0][1].split(":")
                    if not os.path.isabs(file_path):
                        file_path = os.path.join(CONFIG["abs_path"], file_path)
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        with open(file_path, "rb") as fp:
                            code = fp.read()
        else:
            if q != "":
                finder = Finder(CONFIG["data_path"], called = False)
                r = []
                if ID_SP in q:
                    q = q_list[1]
                r = finder.find(q)
                LOG.debug("r: %s", r)
                if r != [] and r != None and r != False:
                    file_path, tmp_line_num = r[0][1].split(":")
                    if not os.path.isabs(file_path):
                        file_path = os.path.join(CONFIG["abs_path"], file_path)
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        with open(file_path, "rb") as fp:
                            pattern = r"func.*%s\ *\(" % q.split(".")[-1]
                            n = 1
                            line = fp.readline()
                            while line != "":
                                code += line
                                flag = re.match(pattern, line)
                                if line_num == 0 and flag != None:
                                    line_num = n
                                line = fp.readline()
                                n += 1

        data = {}
        data["code"] = code
        data["line"] = int(line_num)
        data["path"] = file_path
        file_name = "%s:%s" % (os.path.split(file_path)[-1], line_num)
        self.render("call/view.html", current_nav = "View", file_name = file_name, result = json.dumps(data))

class SearchAjaxHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        query = self.get_argument("q", "").strip()
        size = self.get_argument("size", "10").strip()
        size = int(size)
        results = yield search_index_no_page(IX.ix_func, query + "*", "func", limits = size)
        LOG.debug("result_len: %s", len(results))
        result = []
        for hit in results:
            fields = hit.fields()
            result.append(fields["name"])
            LOG.debug("Doc_id: %s, %s", fields["doc_id"], fields["name"])
        self.write(json.dumps(result))
		