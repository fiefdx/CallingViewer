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

from tornado import gen

from config import CONFIG
from base import BaseHandler
from utils.finder import Finder
from utils.search_whoosh import search_index_no_page
from utils.index_whoosh import IX
from utils.common_utils import sha1sum, escape_html, get_mode, get_definition_from_guru, get_referrers_from_guru, compare_node
from models.project import Project, Projects

LOG = logging.getLogger(__name__)

ID_SP = "____"
SEARCH_IX = IX()

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
                              "text": escape_html(d["name"]),
                              "type": "directory"})
            for f in files:
                nodes.append({"id": os.path.join(project.project_path, f["name"]),
                              "parent": project.project_path,
                              "text": escape_html(f["name"]),
                              "type": "file"})
            nodes.insert(0, parent)
            data["nodes"] = nodes

        self.render("call/call_tree.html", current_nav = "View", version = CONFIG["version"], result = json.dumps(data))

    def post(self):
        project_name = self.get_argument("project_name", "").strip()
        query = self.get_argument("query", "").strip()
        called_str = self.get_argument("called", "false").strip()
        called = True if called_str == "true" else False
        filter_str = self.get_argument("filter", "").strip()
        LOG.debug("query: %s, called: %s, filter: %s", query, called, filter_str)

        data_path = os.path.join(CONFIG["data_path"], "projects", project_name)
        finder = Finder(data_path, called = called)
        r = finder.find(query)

        r_filtered = []
        nodes = []
        tree = []
        if r != None and r != False:
            if filter_str != "":
                for item in r:
                    if filter_str in item[0]:
                        r_filtered.append(item)
            else:
                r_filtered = r

            parent_id = "%s%s%s" % (query, ID_SP, sha1sum(query.decode()))
            if r_filtered != []:
                parent = {"id": parent_id, "parent": "#", "text": query, "type": "tree"}
            else:
                parent = {"id": parent_id, "parent": "#", "text": query, "type": "leaf"}
            for item in r_filtered:
                child_id = "%s%s%s%s%s" % (query, ID_SP, item[0], ID_SP, item[1])
                child_id = "%s%s%s" % (child_id, ID_SP, sha1sum(child_id.decode()))
                item_parts = item[1].split(":")
                src_file = ""
                line_num = ""
                if len(item_parts) == 2:
                    src_file, line_num = item_parts
                elif len(item_parts) == 1:
                    src_file = item_parts[0]
                    line_num = ""
                line_num = int(line_num) if line_num != "" and line_num.isdigit() else 0
                nodes.append({"id": child_id,
                              "parent": parent_id,
                              "src_file": src_file,
                              "num": line_num,
                              "text": escape_html(item[0]),
                              "type": "leaf"})
            parent["size"] = len(nodes)
            tree.append(parent)
            nodes.sort(compare_node)
        LOG.debug("tree: %s", tree)
        data = {}
        data["query"] = query
        data["nodes"] = nodes
        data["tree"] = tree
        data["called"] = called
        data["filter"] = filter_str
        self.write(data)

class CallAjaxHandler(BaseHandler):
    def post(self):
        project_name = self.get_argument("project_name", "").strip()
        query_str = self.get_argument("query", "[]").strip()
        query = json.loads(query_str)
        called_str = self.get_argument("called", "false").strip()
        called = True if called_str == "true" else False
        filter_str = self.get_argument("filter", "").strip()
        LOG.debug("query: %s, called: %s, filter: %s", query, called, filter_str)

        data_path = os.path.join(CONFIG["data_path"], "projects", project_name)
        finder = Finder(data_path, called = called)
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
                size = 0
                for item in r_filtered:
                    size += 1
                    child_id = "%s%s%s%s%s" % (q, ID_SP, item[0], ID_SP, item[1])
                    child_id = "%s%s%s" % (child_id, ID_SP, sha1sum(child_id.decode()))
                    item_parts = item[1].split(":")
                    src_file = ""
                    line_num = ""
                    if len(item_parts) == 2:
                        src_file, line_num = item_parts
                    elif len(item_parts) == 1:
                        src_file = item_parts[0]
                        line_num = ""
                    line_num = int(line_num) if line_num != "" and line_num.isdigit() else 0
                    nodes.append({"id": child_id,
                                  "parent": q_id,
                                  "src_file": src_file,
                                  "num": line_num,
                                  "text": escape_html(item[0]),
                                  "type": "leaf"})
                if r_filtered != []:
                    tree.append({"id": q_id, "size": size})

        nodes.sort(compare_node)
        LOG.debug("tree: %s", tree)
        # LOG.debug("nodes: %s", nodes)
        data = {}
        data["nodes"] = nodes
        data["tree"] = tree
        data["called"] = called
        data["filter"] = filter_str
        self.write(data)

class ViewHandler(BaseHandler):
    def get(self):
        '''
        q like "(*wps.cn/qing/qing/bll.FileSystem).formatSearchedFiles____
                (*wps.cn/qing/qing/bll.FileSystem).Search____
                /home/breeze/Work/QingSearch/src/wps.cn/qing/qing/bll/file.go:1943____
                60eadd760c33a8ae4f8267e5514b342d2a479203"
        '''
        q = self.get_argument("q", "").strip()
        project_name = self.get_argument("p", "").strip()
        d = self.get_argument("d", "false").strip() # definition
        d = True if d == "true" else False
        called_str = self.get_argument("called", "false").strip()
        called = True if called_str == "true" else False
        q_list = []
        if ID_SP in q and len(q.split(ID_SP)) == 4:
            q_list = q.split(ID_SP)
        else:
            q_list = ["", q.split(ID_SP)[0], "", q.split(ID_SP)[-1]]

        LOG.debug("q: %s, d: %s, called: %s", q, d, called)

        file_path, line_num = "Can't open the root element's file!", 0

        data_path = os.path.join(CONFIG["data_path"], "projects", project_name)

        code = ""
        if d == False:
            if q != "":
                q = q_list[-2]

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
                q = q_list[-2]
                file_path, line_num = q.split(":")
                if not os.path.isabs(file_path):
                    file_path = os.path.join(CONFIG["abs_path"], file_path)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    with open(file_path, "rb") as fp:
                        code = fp.read()
            else:
                r = []
                q = q_list[1]
                finder = Finder(data_path, called = True)
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
                finder = Finder(data_path, called = False)
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
                            func_name = q.split(".")[-1]
                            object_name = q.split(".")[-2]
                            star = "[*]" if q[:2] == "(*" else ""
                            if len(object_name) > 0 and object_name[-1] == ")":
                                pattern = r"func[\s]*\([\s]*.*%s[\s]*%s[\s]*\)[\s]*%s[\s]*\(" % (star, object_name[:-1], func_name)
                            else:
                                pattern = r"func[\s]*%s[\s]*\(" % func_name
                            LOG.debug("pattern: %s", pattern)
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
        data["ext"] = os.path.splitext(file_path)[-1].lower()
        data["code"] = code
        data["line"] = int(line_num)
        data["path"] = file_path
        data["project"] = project_name
        file_name = "%s:%s" % (os.path.split(file_path)[-1], line_num)
        self.render("call/view.html", current_nav = "View", file_name = file_name, mode = get_mode(data["ext"]), result = json.dumps(data))

class CodeViewHandler(BaseHandler):
    def get(self):
        '''
        q like q="/home/breeze/Develop/IDGO/src/github.com/flike/idgo/server/server.go:40:2"
        '''
        q = self.get_argument("q", "").strip()
        project_name = self.get_argument("p", "").strip()

        LOG.debug("q: %s, p: %s", q, project_name)

        file_path, line_num = "Can't open the root element's file!", 0

        code = ""
        if q != "":
            if ":" in q:
                file_path, line_num, ch = q.split(":")
            if not os.path.isabs(file_path):
                file_path = os.path.join(CONFIG["abs_path"], file_path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, "rb") as fp:
                    code = fp.read()

        data = {}
        data["ext"] = os.path.splitext(file_path)[-1].lower()
        data["code"] = code
        data["line"] = int(line_num)
        data["path"] = file_path
        data["project"] = project_name
        file_name = "%s:%s" % (os.path.split(file_path)[-1], line_num)
        self.render("call/view.html", current_nav = "View", file_name = file_name, mode = get_mode(data["ext"]), result = json.dumps(data))

class GoToDefinitionAjaxHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        file_path = self.get_argument("file_path", "").strip()
        query = self.get_argument("q", "").strip()
        line = self.get_argument("line", "0").strip()
        ch = self.get_argument("ch", "0").strip()
        project_name = self.get_argument("project_name", "").strip()
        line = int(line)
        ch = int(ch)
        LOG.debug("project_name: %s, q: %s, line: %s, ch: %s", project_name, query, line, ch)

        projects = Projects()
        data = {}
        data["project"] = project_name
        data["file_path"] = ""
        data["desc"] = ""
        project = Project()
        project.parse_dict(projects.get(project_name))
        os.environ["GOPATH"] = project.go_path
        LOG.debug("GOPATH: %s", project.go_path)

        r = get_definition_from_guru(file_path, line, ch)
        if r:
            if r.has_key("definition") and r["definition"].has_key("objpos"):
                data["file_path"] = r["definition"]["objpos"]
            elif r.has_key("objpos"):
                data["file_path"] = r["objpos"]
            else:
                data["file_path"] = ""
            data["desc"] = r["definition"]["desc"] if r.has_key("definition") and r["definition"].has_key("desc") else ""
        LOG.debug("GoToDefinition: %s", data)

        self.write(data)

class FindReferrersAjaxHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        file_path = self.get_argument("file_path", "").strip()
        query = self.get_argument("q", "").strip()
        line = self.get_argument("line", "0").strip()
        ch = self.get_argument("ch", "0").strip()
        project_name = self.get_argument("project_name", "").strip()
        line = int(line)
        ch = int(ch)
        LOG.debug("project_name: %s, q: %s, line: %s, ch: %s", project_name, query, line, ch)

        projects = Projects()
        data = {}
        data["project"] = project_name
        data["file_path"] = ""
        data["desc"] = ""
        data["refs"] = []
        project = Project()
        project.parse_dict(projects.get(project_name))
        os.environ["GOPATH"] = project.go_path
        LOG.debug("GOPATH: %s", project.go_path)

        r = get_referrers_from_guru(file_path, line, ch)
        if isinstance(r, list):
            data["file_path"] = r[0]["objpos"] if len(r) > 0 and r[0].has_key("objpos") else ""
            data["desc"] = r[0]["desc"] if len(r) > 0 and r[0].has_key("desc") else ""
            data["refs"] = []
            if len(r) > 1:
                for package in r[1:]:
                    if package.has_key("refs"):
                        for ref in package["refs"]:
                            if ref.has_key("pos"):
                                data["refs"].append(ref["pos"])
        elif isinstance(r, map):
            data["file_path"] = r["referrers"]["objpos"] if r.has_key("referrers") and r["referrers"].has_key("objpos") else ""
            data["desc"] = r["referrers"]["desc"] if r.has_key("referrers") and r["referrers"].has_key("desc") else ""
            data["refs"] = r["referrers"]["refs"] if r.has_key("referrers") and r["referrers"].has_key("refs") else []
        LOG.debug("FindReferrers: %s", data)

        self.write(data)

class SearchAjaxHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        query = self.get_argument("q", "").strip()
        project_name = self.get_argument("p", "").strip()
        size = self.get_argument("size", "10").strip()
        size = int(size)
        results = yield search_index_no_page(SEARCH_IX.get(project_name), query + "*", "call", limits = size)
        LOG.debug("result_len: %s", len(results))
        result = []
        for hit in results:
            fields = hit.fields()
            result.append(fields["name"])
            LOG.debug("Doc_id: %s, %s", fields["doc_id"], fields["name"])
        self.write(json.dumps(result))
