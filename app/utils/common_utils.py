# -*- coding: utf-8 -*-
'''
Created on 2016-07-20
@summary:  some utils
@author: YangHaitao
'''

import os
import logging
import time
import json
import hashlib
from subprocess import Popen, PIPE, STDOUT

from utils import errors

LOG = logging.getLogger(__name__)

GURU = {}

def sha1sum(content):
    '''
    param content must be unicode
    result is unicode
    '''
    m = hashlib.sha1(content.encode("utf-8"))
    m.digest()
    result = m.hexdigest().decode("utf-8")
    return result

def sha256sum(content):
    '''
    param content must be unicode
    result is unicode
    '''
    m = hashlib.sha256(content.encode("utf-8"))
    m.digest()
    result = m.hexdigest().decode("utf-8")
    return result

def md5twice(content):
    '''
    param content must be unicode
    result is unicode
    '''
    m = hashlib.md5(content.encode("utf-8")).hexdigest()
    result = hashlib.md5(m).hexdigest().decode("utf-8")
    return result

def make_callgraph_data(main_path, data_path):
    result = False
    cmd = r'callgraph -algo=cha -format="\"{{.Caller}}\" \"{{.Callee}}\" \"{{.Filename}}:{{.Line}}\"" %s > %s'
    LOG.debug("cmd: %s", cmd % (main_path, data_path))
    try:
        p = Popen(cmd % (main_path, data_path), shell = True)
        p.wait()
        result = True
    except Exception, e:
        LOG.exception(e)
    return result

def check_guru():
    cmd = r'guru -help'
    try:
        p = Popen(cmd, shell = True, stdout = PIPE, stderr = STDOUT)
        p.wait()
        r = p.stdout.read()
        LOG.debug("check_guru: %s", r)
        if "-json" in r:
            GURU["-json"] = True
            GURU["cmd"] = "guru"
        elif "-format" in r:
            GURU["-format"] = True
            GURU["cmd"] = "guru"
        else:
            cmd = r'golang-guru -help'
            p = Popen(cmd, shell = True, stdout = PIPE, stderr = STDOUT)
            p.wait()
            r = p.stdout.read()
            LOG.debug("check_guru: %s", r)
            if "-json" in r:
                GURU["-json"] = True
                GURU["cmd"] = "golang-guru"
            elif "-format" in r:
                GURU["-format"] = True
                GURU["cmd"] = "golang-guru"
            else:
                raise errors.GuruNotFoundError
    except Exception, e:
        LOG.exception(e)

def get_definition_from_guru(file_path, line, ch):
    '''
    line: offset from 0
    ch: offset from 0
    '''
    result = False
    if GURU.has_key("cmd"):
        cmd = r"%s" % GURU["cmd"]
    else:
        raise errors.GuruNotFoundError
    if GURU.has_key("-json"):
        cmd += r' -reflect -json definition %s:#%s'
    else:
        cmd += r' -reflect -format json definition %s:#%s'
    fp = open(file_path, "rb")
    offset = 0
    for l in xrange(line):
        offset += len(fp.readline())
    offset += ch
    LOG.debug("cmd: %s", cmd % (file_path, offset))
    try:
        p = Popen(cmd % (file_path, offset), shell = True, stdout = PIPE)
        p.wait()
        result = json.loads(p.stdout.read())
        LOG.debug("get_definition_from_guru: %s", result)
    except Exception, e:
        LOG.exception(e)
    return result

def get_referrers_from_guru(file_path, line, ch):
    '''
    line: offset from 0
    ch: offset from 0
    '''
    result = False
    if GURU.has_key("cmd"):
        cmd = r"%s" % GURU["cmd"]
    else:
        raise errors.GuruNotFoundError
    if GURU.has_key("-json"):
        cmd += r' -reflect -json referrers %s:#%s'
    else:
        cmd += r' -reflect -format json referrers %s:#%s'
    fp = open(file_path, "rb")
    offset = 0
    for l in xrange(line):
        offset += len(fp.readline())
    offset += ch
    LOG.debug("cmd: %s", cmd % (file_path, offset))
    try:
        p = Popen(cmd % (file_path, offset), shell = True, stdout = PIPE)
        p.wait()
        lines = p.stdout.readlines()
        try:
            result = json.loads("".join(lines))
        except Exception, e:
            json_str = "["
            for line in lines:
                if line == "}\n":
                    json_str += "},\n"
                else:
                    json_str += line
            if json_str[-2:] == ",\n":
                json_str = json_str[:-2]
            elif json_str[-2:] == ",":
                json_str = json_str[:-1]
            json_str += "\n]"
            LOG.debug("get_referrers_from_guru json_str: %s", json_str)
            result = json.loads(json_str)
        LOG.debug("get_referrers_from_guru: %s", result)
    except Exception, e:
        LOG.exception(e)
    return result


def get_file_size(size):
    result = ""
    try:
        if size > 1024*1014*1024:
            result = "%.3f G"%(size/1024.0/1024.0/1024.0)
        elif size > 1024*1024:
            result = "%.3f M"%(size/1024.0/1024.0)
        elif size > 1024:
            result = "%.3f K"%(size/1024.0)
        else:
            result = "%d B"%size
    except Exception, e:
        LOG.exception(e)
        result = "0 B"
    return result

def escape_html(content):
    # content = content.replace('\r', '')
    # content = content.replace('\n', ' ')
    content = content.replace('&','&amp;')
    content = content.replace('<','&lt;')
    content = content.replace('>','&gt;')
    # content = content.replace(' ','&nbsp;')
    content = content.replace('\"','&quot;')
    return content

def makekey(c):
    if isinstance(c, (int, long)):
        return c
    elif isinstance(c, (str, unicode)):
        return c.lower()

def listsort(dirs, files, sort_by = "name", desc = False):
    dirs_keys = []
    dirs_tree = {}
    dirs_sort = []
    files_keys = []
    files_tree = {}
    files_sort = []
    for d in dirs:
        dirs_keys.append(d[sort_by])
        if dirs_tree.has_key(d[sort_by]):
            dirs_tree[d[sort_by]].append(d)
        else:
            dirs_tree[d[sort_by]] = []
            dirs_tree[d[sort_by]].append(d)
    dirs_keys = list(set(dirs_keys))
    dirs_keys.sort(key = makekey, reverse = desc)
    # LOG.info("Dirs_keys: %s", dirs_keys)
    n = 1
    for k in dirs_keys:
        for d in dirs_tree[k]:
            d["num"] = n
            d["size"] = get_file_size(d["size"])
            dirs_sort.append(d)
            n += 1
    for f in files:
        files_keys.append(f[sort_by])
        if files_tree.has_key(f[sort_by]):
            files_tree[f[sort_by]].append(f)
        else:
            files_tree[f[sort_by]] = []
            files_tree[f[sort_by]].append(f)
    files_keys = list(set(files_keys))
    files_keys.sort(key = makekey, reverse = desc)
    # LOG.info("Files_keys: %s", files_keys)
    for k in files_keys:
        for f in files_tree[k]:
            f["num"] = n
            f["size"] = get_file_size(f["size"])
            files_sort.append(f)
            n += 1
    return (dirs_sort, files_sort)

def listdir(dir_path = ".", sort_by = "name", desc = False):
    dirs = []
    files = []
    try:
        dirs_list = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
        files_list = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        dirs_list.sort()
        files_list.sort()
        n = 1
        for d in dirs_list:
            d_path = os.path.join(dir_path, d)
            dirs.append({
                "num":n,
                "name":d,
                "sha1":sha1sum(d_path),
                "type":"Directory",
                "size":os.path.getsize(d_path),
                "ctime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(d_path))),
                "mtime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(d_path)))
            })
            n += 1
        for f in files_list:
            f_path = os.path.join(dir_path, f)
            files.append({
                "num":n,
                "name":f,
                "sha1":sha1sum(f_path),
                "type":os.path.splitext(f)[-1],
                "size":os.path.getsize(f_path),
                "ctime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(f_path))),
                "mtime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(f_path)))
            })
            n += 1
    except Exception, e:
        LOG.exception(e)
    return listsort(dirs, files, sort_by = sort_by, desc = desc)

def get_mode(ext):
    mode_map = {".go": "text/x-go",
                ".php": "text/x-php",
                ".py": "text/x-python",
                ".cpy": "text/x-cython",
                ".java": "text/x-java:",
                ".cc": "text/x-c++src",
                ".hpp": "text/x-c++src",
                ".cpp": "text/x-c++src",
                ".c": "text/x-csrc",
                ".h": "text/x-csrc",
                ".css": "text/x-scss",
                ".sh": "text/x-sh",
                ".js": "text/javascript",
                ".html": "text/html",
                ".xml": "text/html",
                ".json": "application/json",
                ".sql": "text/x-sql",
                ".yml": "text/x-yaml",
                ".toml": "text/x-toml",
                ".md": "text/x-markdown",
                ".lua": "text/x-lua"}
    if ext.lower() in mode_map:
        return mode_map[ext]
    else:
        return ""

def compare_node(n0, n1):
    src_file_cmp = cmp(n0["src_file"], n1["src_file"])
    if src_file_cmp != 0:
        return src_file_cmp
    else:
        return cmp(n0["num"], n1["num"])
