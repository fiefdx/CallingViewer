# -*- coding: utf-8 -*-
'''
Created on 2016-07-20
@summary: whoosh index
@author: YangHaitao
'''

import os
import sys
import os.path
import time
import logging
import shutil
import json
import whoosh
from whoosh import index
from whoosh.filedb.filestore import FileStorage
from whoosh.fields import Schema, ID, TEXT, STORED
from whoosh.analysis import CharsetFilter, StemmingAnalyzer
from whoosh.support.charset import accent_map
from whoosh.writing import AsyncWriter

import jieba
# jieba.initialize()
from jieba.analyse import ChineseAnalyzer
analyzer = ChineseAnalyzer()

from models.item import FUNC
from config import CONFIG


LOG = logging.getLogger(__name__)


class IX(object):
    func = "func"
    IX_NAMES = ["func", ]

    ix_func = None
    IX_INDEXS = ["ix_func", ]

    def __init__(self, init_object = True):
        for n, ix_index_attr in enumerate(IX.IX_INDEXS):
            try:
                if hasattr(IX, ix_index_attr) and getattr(IX, ix_index_attr) == None:
                    setattr(IX, 
                            ix_index_attr, 
                            get_whoosh_index(CONFIG["index_root_path"], 
                                             getattr(IX, IX.IX_NAMES[n])))
                    LOG.info("Init %s success", IX.IX_INDEXS[n])
                else:
                    LOG.info("Inited %s success", IX.IX_INDEXS[n])
            except Exception, e:
                LOG.info("Init %s failed", IX.IX_INDEXS[n])
                LOG.exception(e)
        if init_object:
            self.ix_func = get_whoosh_index(CONFIG["index_root_path"], IX.func)
        else:
            self.ix_func = None

    @classmethod
    def content(cls):
        return "IX: ix_func: %s" % (cls.ix_func)

    @classmethod
    def cls_close(cls):
        for n, ix_index_attr in enumerate(cls.IX_INDEXS):
            try:
                if hasattr(cls, ix_index_attr) and getattr(cls, ix_index_attr):
                    getattr(cls, ix_index_attr).close()
                    setattr(cls, ix_index_attr, None)
                LOG.info("Close %s success", ix_index_attr)
            except Exception, e:
                LOG.info("Close %s failed", ix_index_attr)
                LOG.exception(e)

    def close(self):
        for ix_index_attr in IX.IX_INDEXS:
            try:
                if hasattr(self, ix_index_attr) and getattr(self, ix_index_attr):
                    getattr(self, ix_index_attr).close()
                LOG.info("Close %s success", ix_index_attr)
            except Exception, e:
                LOG.info("Close %s failed", ix_index_attr)
                LOG.exception(e)

def get_whoosh_index(index_path, index_name = ""):
    result = None
    try:
        if index_name != "":
            sch = {"func": Schema(doc_id = ID(unique = True, stored = True), 
                                  name = TEXT(analyzer = analyzer, stored = True)),
                   }
            schema = sch[index_name]
            index_path = os.path.join(index_path, index_name)
            LOG.debug("Index path: %s" % index_path)
            if not os.path.exists(index_path):
                os.makedirs(index_path)
                ix = index.create_in(index_path, schema = schema, indexname = index_name)
                LOG.debug("Create index[%s, %s]" % (index_path, index_name))
                result = ix
            else:
                flag = index.exists_in(index_path, indexname = index_name)
                if flag == True:
                    ix = index.open_dir(index_path, indexname = index_name)
                    LOG.debug("Open index[%s, %s]" % (index_path, index_name))
                    result = ix
                else:
                    ix = index.create_in(index_path, schema = schema, indexname = index_name)
                    LOG.debug("Create index[%s, %s]" % (index_path, index_name))
                    result = ix
        else:
            LOG.warning("Lost index name, so return None!")
    except Exception, e:
        LOG.exception(e)
        result = False
    return result

def update_whoosh_index_doc(index, item, index_name, merge = False):
    result = False
    try:
        if index != None and index != False:
            try:
                # writer = index.writer()
                writer = AsyncWriter(index)
                if index_name == "func":
                    writer.update_document(doc_id = unicode(str(item.id)), 
                                           name = item.name)
                else:
                    LOG.error("index_name error: in the update_whoosh_index_doc!")
                writer.commit(merge = merge)
                LOG.debug("Update index[%s] doc_id[%s]"%(index_name, item.id))
                result = True
            except Exception, e:
                LOG.exception(e)
                writer.cancel()
                result = False
    except Exception, e:
        LOG.exception(e)
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
                    if index_name == "func":
                        writer.update_document(doc_id = unicode(str(item.id)), 
                                               name = item.name)
                    else:
                        LOG.error("index_name error: in the update_whoosh_index_doc_num!")
                    LOG.debug("Update index[%s] doc_id[%s]"%(index_name, item.id))
                    if n == item_num:
                        writer.commit(merge = merge)
                        LOG.info("Commit index[%s] success."%index_name)
                        # writer = index.writer()
                        writer = AsyncWriter(index)
                        n = 0
                if n % item_num != 0:
                    s = time.time()
                    writer.commit(merge = merge)
                    ss = time.time()
                    LOG.debug("Commit use %ss", ss - s)
                    LOG.info("Commit index[%s] success."%index_name)
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

def delete_whoosh_index_doc_num(index, item_iter, item_num, index_name, merge = False):
    result = False
    try:
        if index != None and index != False:
            n = 0
            # writer = index.writer()
            writer = AsyncWriter(index)
            try:
                for item in item_iter:
                    n += 1
                    if index_name == "func":
                        writer.delete_by_term("doc_id", unicode(str(item.id)))
                    else:
                        LOG.error("index_name error: in the delete_whoosh_index_doc_num!")
                    LOG.debug("Delete index[%s] doc_id[%s]"%(index_name, item.id))
                    if n == item_num:
                        writer.commit(merge = merge)
                        LOG.info("Commit index[%s] success."%index_name)
                        # writer = index.writer()
                        writer = AsyncWriter(index)
                        n = 0
                if n % item_num != 0:
                    writer.commit(merge = merge)
                    LOG.info("Commit index[%s] success."%index_name)
                result = True
            except Exception, e:
                LOG.exception(e)
                writer.cancel()
                result = False
    except Exception, e:
        LOG.exception(e)
    return result

def delete_whoosh_index_doc(index, doc_id, index_name, merge = False):
    result = False
    try:
        if index != None and index != False:
            try:
                # writer = index.writer()
                writer = AsyncWriter(index)
                writer.delete_by_term("doc_id", doc_id)
                writer.commit(merge = merge)
                LOG.debug("Delete index[%s] doc_id[%s]"%(index_name, doc_id))
                result = True
            except Exception, e:
                LOG.exception(e)
                writer.cancel()
                result = False
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

def index_all_func(db, ix = None, merge = False):
    result = False
    if ix == None:
        ix = IX
    try:
        flag = update_whoosh_index_doc_num(ix.ix_func, func_iter(db), 1000, "func", merge = False)
        if flag:
            LOG.debug("Index func success.")
        else:
            LOG.debug("Index func failed.")
        result = True
    except Exception, e:
        LOG.exception(e)
    return result
