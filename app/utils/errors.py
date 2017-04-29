# -*- coding: utf-8 -*-
'''
Created on 2017-04-29
@summary: errors
@author: YangHaitao
'''

class InvalidParamsError(Exception):
    def __str__(self):
        return "InvalidParamsError"

    def __repr__(self):
        return "InvalidParamsError"

class AddProjectError(Exception):
    def __str__(self):
        return "AddProjectError"

    def __repr__(self):
        return "AddProjectError"

class ExistProjectError(Exception):
    def __str__(self):
        return "ExistProjectError"

    def __repr__(self):
        return "ExistProjectError"

class EditProjectError(Exception):
    def __str__(self):
        return "EditProjectError"

    def __repr__(self):
        return "EditProjectError"

class DeleteProjectError(Exception):
    def __str__(self):
        return "DeleteProjectError"

    def __repr__(self):
        return "DeleteProjectError"

class ReindexProjectError(Exception):
    def __str__(self):
        return "ReindexProjectError"

    def __repr__(self):
        return "ReindexProjectError"