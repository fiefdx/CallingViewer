# -*- coding: utf-8 -*-
'''
Created on 2016-06-24
@summary: finder
@author: YangHaitao
'''

import os
import logging
import json

from config import CONFIG

if CONFIG["db_type"] == "leveldb":
    from db.leveldb_interface import FileStorage2 as FS
elif CONFIG["db_type"] == "bsddb":
    from db.bsddb_interface import FileStorage2 as FS
else:
    from db.leveldb_interface import FileStorage2 as FS

LOG = logging.getLogger(__name__)

class Func(object):
    def __init__(self, func):
        self.func = func[0]
        self.src = func[1]
        self.recursion = False

    def set_recursion(self, recursion = True):
        self.recursion = recursion

    def to_dict(self):
        return {self.func: self.recursion}

    def to_str(self):
        if self.recursion:
            return str(self.to_dict()) + " @ %s" % self.src
        else:
            return self.func + " @ %s" % self.src

    def __str__(self):
        return str(self.to_str())

    def __repr__(self):
        return str(self.to_str())


class Finder(object):
    def __init__(self, data_path, called = True):
        self.data_path = data_path
        self.fpath = os.path.join(data_path, "data.callgraph")
        self.data = {}
        self.called = called
        if self.called == True:
            self.db = FS(data_path, "table_called.db")
        else:
            self.db = FS(data_path, "table_calling.db")

    def build_finder(self):
        fp = open(self.fpath, "rb")
        n = 1
        line = fp.readline()
        if self.called == True:
            while line != "":
                LOG.debug("processing: line: %s", n)
                line = line.strip()
                caller, callee, src_path = line.split(" ")
                caller = caller.replace("\"", "")
                callee = callee.replace("\"", "")
                src_path = src_path.replace("\"", "")
                try:
                    value = []
                    value = json.loads(self.db.get(callee))
                    index = self.has_child(value, [caller, src_path])
                    if index == -1:
                        value.append([caller, src_path])
                        self.db.put(callee, json.dumps(value))
                    elif int(value[index][1].split(":")[-1]) > int(src_path.split(":")[-1]):
                        value[index][1] = src_path
                except KeyError:
                    self.db.put(callee, json.dumps([[caller, src_path]]))
                line = fp.readline()
                n += 1
        else:
            while line != "":
                LOG.debug("processing: line: %s", n)
                line = line.strip()
                caller, callee, src_path = line.split(" ")
                caller = caller.replace("\"", "")
                callee = callee.replace("\"", "")
                src_path = src_path.replace("\"", "")
                try:
                    value = []
                    value = json.loads(self.db.get(caller))
                    index = self.has_child(value, [callee, src_path])
                    if index == -1 :
                        value.append([callee, src_path])
                        self.db.put(caller, json.dumps(value))
                    elif int(value[index][1].split(":")[-1]) > int(src_path.split(":")[-1]):
                        value[index][1] = src_path
                except KeyError:
                    self.db.put(caller, json.dumps([[callee, src_path]]))
                line = fp.readline()
                n += 1
        fp.close()

    def has_child(self, parent, child):
        for n, c in enumerate(parent):
            if c[0] == child[0]:
                return n
        return -1

    def find(self, callee):
        result = []
        try:
            value = self.db.get(callee)
            result = json.loads(value)
            LOG.debug("Result: %s", result)
        except KeyError:
            result = None
        except Exception, e:
            LOG.exception(e)
            result = False
        return result

    def find_all_relation(self, callee):
        out_name = ".called.rel" if self.called == True else ".calling.rel"
        out_path = os.path.join(self.data_path,
                                "tmp",
                                callee.replace("/", ".").replace("*", "_") + out_name)
        self.out = open(out_path, "wb")
        self.traverse_func([callee, ""])
        self.out.close()

    def traverse(self, callee, relation = []):
        if callee in relation:
            LOG.warning("Have loop: %s", relation + [callee, ])
            return
        relation.append(callee)
        callers = self.find(callee)
        if callers != [] and callers != False:
            for caller in callers:
                self.traverse(caller, relation = relation)
        elif callers == []:
            tmp_relation = []
            for r in relation:
                tmp_relation.append(" @ ".join(r))
            self.out.write(" -> ".join(tmp_relation) + "\n")
            LOG.debug("Relation: %s", relation)
        else:
            pass
        relation.pop()

    def traverse_func(self, callee, relation = {"relation": [], "relation_func": []}, n = 0, filter_string = "wps.cn"):
        if n > CONFIG["max_recursion"]:
            return
        n += 1
        if filter_string not in callee[0]:
            return
        callee_func = Func(callee)
        if callee in relation["relation"]:
            for f in relation["relation_func"]:
                if f.func == callee[0]:
                    f.set_recursion()
            callee_func.set_recursion()
            LOG.warning("Have recursion: %s", callee_func)
            return
        relation["relation"].append(callee)
        relation["relation_func"].append(callee_func)
        callers = self.find(callee[0])
        if callers != [] and callers != False:
            for caller in callers:
                self.traverse_func(caller, relation = relation, n = n)
        elif callers == []:
            relation_list = [str(r) for r in relation["relation_func"]]
            self.out.write(" -> ".join(relation_list) + "\n")
            LOG.debug("Relation: %s", relation["relation"])
        else:
            pass
        n -= 1
        relation["relation"].pop()
        relation["relation_func"].pop()
