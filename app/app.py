# -*- coding: utf-8 -*-
'''
Created on 2015-09-18
@summary: app
@author: YangHaitao
'''

import os
import os.path
import logging

import tornado.web

import modules.bootstrap as bootstrap
import handlers.test as test
from config import CONFIG
from handlers import test
from handlers import call
from handlers import project
from handlers import listdir

cwd = os.path.split(os.path.realpath(__file__))[0]

LOG = logging.getLogger(__name__)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", call.CallHandler),
                    (r"/leaf", call.CallAjaxHandler),
                    (r"/search", call.SearchAjaxHandler),
                    (r"/view", call.ViewHandler),
                    (r"/code/view", call.CodeViewHandler),
                    (r"/add/project", project.ProjectAjaxAddHandler),
                    (r"/edit/project", project.ProjectAjaxEditHandler),
                    (r"/reindex/project", project.ProjectAjaxReindexHandler),
                    (r"/select/project", project.ProjectAjaxSelectHandler),
                    (r"/delete/project", project.ProjectAjaxDeleteHandler),
                    (r"/project/leaf", project.ProjectAjaxLeafHandler),
                    (r"/project/view", project.ViewHandler),
                    (r"/project/definition", call.GoToDefinitionAjaxHandler),
                    (r"/project/referrers", call.FindReferrersAjaxHandler),
                    (r"/listdir", listdir.ListDirHandler),
                    (r"/test", test.TestHandler),
                    ]
        settings = dict(debug = CONFIG["app_debug"],
                        template_path = os.path.join(cwd, "templates"),
                        static_path = os.path.join(cwd, "static"),
                        ui_modules = [bootstrap,])
        tornado.web.Application.__init__(self, handlers, **settings)
