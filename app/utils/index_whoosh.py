# -*- coding: utf-8 -*-
'''
Created on 2016-07-20
@summary: whoosh index
@author: YangHaitao
'''

import os
import os.path
import time
import logging
import shutil

from whoosh import index
from whoosh.fields import Schema, ID, TEXT
from whoosh.writing import AsyncWriter

# jieba.initialize()
from jieba.analyse import ChineseAnalyzer
analyzer = ChineseAnalyzer()

from models.item import FUNC
from config import CONFIG

LOG = logging.getLogger(__name__)

class IX(object):
    IX_INDEXS = {}

    def __init__(self, projects = []):
        for p in projects:
            try:
                if IX.IX_INDEXS.has_key(p["project_name"]) and IX.IX_INDEXS[p["project_name"]]:
                    LOG.info("Inited %s success", p["project_name"])
                else:
                    index_path = os.path.join(CONFIG["data_path"], "projects", p["project_name"], "index")
                    IX.IX_INDEXS[p["project_name"]] = get_whoosh_index(index_path, "call")
                    LOG.info("Init %s success", p["project_name"])
            except Exception, e:
                LOG.info("Init %s failed", p["project_name"])
                LOG.exception(e)

    @classmethod
    def cls_close(cls):
        for k in cls.IX_INDEXS:
            try:
                cls.IX_INDEXS[k].close()
                cls.IX_INDEXS[k] = None
                LOG.info("Close %s success", k)
            except Exception, e:
                LOG.info("Close %s failed", k)
                LOG.exception(e)

    def get(self, project_name):
        if IX.IX_INDEXS.has_key(project_name):
            return IX.IX_INDEXS[project_name]
        else:
            return None

    def add(self, project_name):
        result = False
        try:
            index_path = os.path.join(CONFIG["data_path"], "projects", project_name, "index")
            IX.IX_INDEXS[project_name] = get_whoosh_index(index_path, "call")
            LOG.info("Init %s success", project_name)
            result = True
        except Exception, e:
            LOG.exception(e)
        return result

    def delete(self, project_name):
        result = False
        try:
            if IX.IX_INDEXS.has_key(project_name):
                index_path = os.path.join(CONFIG["data_path"], "projects", project_name, "index")
                if os.path.exists(index_path) and os.path.isdir(index_path):
                    shutil.rmtree(index_path)
                del(IX.IX_INDEXS[project_name])
            result = True
        except Exception, e:
            LOG.exception(e)
        return result

    def close(self):
        for k in IX.IX_INDEXS:
            try:
                IX.IX_INDEXS[k].close()
                LOG.info("Close %s success", k)
            except Exception, e:
                LOG.info("Close %s failed", k)
                LOG.exception(e)

def get_whoosh_index(index_path, index_name = ""):
    result = None
    try:
        if index_name != "":
            sch = {"call": Schema(doc_id = ID(unique = True, stored = True), 
                                  name = TEXT(analyzer = analyzer, stored = True)),
                   }
            schema = sch[index_name]
            index_path = os.path.join(index_path, index_name)
            LOG.debug("Index path: %s", index_path)
            if not os.path.exists(index_path):
                os.makedirs(index_path)
                ix = index.create_in(index_path, schema = schema, indexname = index_name)
                LOG.debug("Create index[%s, %s]", index_path, index_name)
                result = ix
            else:
                flag = index.exists_in(index_path, indexname = index_name)
                if flag == True:
                    ix = index.open_dir(index_path, indexname = index_name)
                    LOG.debug("Open index[%s, %s]", index_path, index_name)
                    result = ix
                else:
                    ix = index.create_in(index_path, schema = schema, indexname = index_name)
                    LOG.debug("Create index[%s, %s]", index_path, index_name)
                    result = ix
        else:
            LOG.warning("Lost index name, so return None!")
    except Exception, e:
        LOG.exception(e)
        result = False
    return result

def update_whoosh_index_doc_num(index, item_iter, item_num, index_name, merge = False):
    result = False
    try:
        if index != None and index != False:
            n = 0
            # writer = index.writer()
            writer = AsyncWriter(index)
            try:
                for item in item_iter:
                    n += 1
                    if index_name == "call":
                        writer.update_document(doc_id = unicode(str(item.id)), 
                                               name = item.name)
                    else:
                        LOG.error("index_name error: in the update_whoosh_index_doc_num!")
                    LOG.debug("Update index[%s] doc_id[%s]", index_name, item.id)
                    if n == item_num:
                        writer.commit(merge = merge)
                        LOG.info("Commit index[%s] success.", index_name)
                        # writer = index.writer()
                        writer = AsyncWriter(index)
                        n = 0
                if n % item_num != 0:
                    s = time.time()
                    writer.commit(merge = merge)
                    ss = time.time()
                    LOG.debug("Commit use %ss", ss - s)
                    LOG.info("Commit index[%s] success.", index_name)
                result = True
            except Exception, e:
                LOG.exception(e)
                writer.cancel()
                result = False
        else:
            LOG.error("index object is False or None!")
    except Exception, e:
        LOG.exception(e)
    return result

def delete_whoosh_index(index_path, index_name):
    result = False
    try:
        index_path = os.path.join(index_path, index_name)
        if os.path.exists(index_path) and os.path.isdir(index_path):
            shutil.rmtree(index_path)
            result = True
        else:
            result = True
    except Exception, e:
        LOG.exception(e)
    return result

#
# index for func
#

def func_iter(db):
    for key, value in db.range_iter():
        func_item = FUNC()
        func_item.name = key
        func_item.generate_id()
        yield func_item

def index_all_func(db, ix, name = "call", bulk = 10000, merge = False):
    result = False
    try:
        flag = update_whoosh_index_doc_num(ix, func_iter(db), bulk, name, merge = False)
        if flag:
            LOG.debug("Index %s success", name)
        else:
            LOG.debug("Index %s failed", name)
        result = True
    except Exception, e:
        LOG.exception(e)
    return result
