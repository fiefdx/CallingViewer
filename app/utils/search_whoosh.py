# -*- coding: utf-8 -*-
'''
Created on 2016-07-20
@summary: whoosh search
@author: YangHaitao
'''

import logging

from tornado import gen

from whoosh import index
from whoosh.qparser import MultifieldParser
from whoosh.highlight import HtmlFormatter

LOG = logging.getLogger(__name__)

@gen.coroutine
def search_index_page(index, query, index_name, page, limits, filter = None):
    result = []
    try:
        search_field = {"func": ["name"]}
        searcher = index.searcher()
        mparser = MultifieldParser(search_field[index_name], schema = index.schema)
        q = mparser.parse(query)
        # result = searcher.search(q, filter = filter)
        result = searcher.search_page(q, page, pagelen = limits)
    except Exception, e:
        LOG.exception(e)
        result = False
    # return result
    raise gen.Return(result)

@gen.coroutine
def search_index_no_page(index, query, index_name, limits = None, filter = None):
    result = []
    try:
        search_field = {"call": ["name"]}
        searcher = index.searcher()
        mparser = MultifieldParser(search_field[index_name], schema = index.schema)
        q = mparser.parse(query)
        result = searcher.search(q, filter = filter, limit = limits)
    except Exception, e:
        LOG.exception(e)
        result = False
    # return result
    raise gen.Return(result)

@gen.coroutine
def search_query_page(ix, query_string, index_name, page = 0, limits = None):
    result = {"result":[], "totalcount": 0}
    try:
        query_string = query_string
        LOG.debug("Query_string: %s", query_string)
        hf = HtmlFormatter(tagname="em", classname="match", termclass="term")
        results = yield search_index_page(ix, query_string, index_name, page, limits)
        results.results.formatter = hf
        results.results.fragmenter.charlimit = 100*1024
        results.results.fragmenter.maxchars = 20
        # results.results.fragmenter.surround = 5
        results_len = 0
        if results.results.has_exact_length():
            results_len = len(results)
        LOG.debug("Have %s results:", results_len)
        results_len = len(results)
        result["totalcount"] = results_len
        LOG.debug("Have %s results:", results_len)
        results_num = 0
        for hit in results:
            item = ThumbnailItem()
            results_num += 1
            LOG.debug("Result: %s", results_num)
            fields = hit.fields()
            LOG.debug("Doc_id: %s", fields["doc_id"])
            html = sqlite.get_html_by_id(fields["doc_id"], conn = DB.conn_html)
            title = hit.highlights("file_name", text = html.file_name[0:-5])
            item.title = title if title.strip() != "" else html.file_name[0:-5]
            item.title = html.file_name
            item.excerpts = hit.highlights("file_content", top = 5, text = html.file_content)
            item.url = "/view/html/%s" % html.sha1
            item.date_time = html.updated_at
            item.description = html.updated_at[0:19]
            result["result"].append(item)
            yield gen.moment
    except Exception, e:
        LOG.exception(e)
        result = False
    # return result
    raise gen.Return(result)
