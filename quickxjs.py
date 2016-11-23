#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: lonewolf
# Date: 2013-10-26 11:23:48
# 
import sublime
import sublime_plugin
import functools
import os
import datetime
import json
import re
import subprocess
import sys
import time
import codecs
import getpass
try:
    import helper
    import rebuild
except ImportError:
    from . import helper
    from . import rebuild

TEMP_PATH="" 

jsTemplate="""/*
* Author: ${author}
* Date: ${date}
* Desc: 
**/
"""

# init plugin,load definitions
def init():
    global TEMP_PATH
    TEMP_PATH=sublime.packages_path()+"/User/QuickXJs.cache"


class JsNewFileCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.window.run_command("hide_panel")
        title = "untitle"
        on_done = functools.partial(self.on_done, dirs[0])
        v = self.window.show_input_panel(
            "File Name:", title + ".js", on_done, None, None)
        v.sel().clear()
        v.sel().add(sublime.Region(0, len(title)))

    def on_done(self, path, name):
        filePath = os.path.join(path, name)
        if os.path.exists(filePath):
            sublime.error_message("Unable to create file, file exists.")
        else:
            code = jsTemplate
            # add attribute
            format = "%Y-%m-%d %H:%M:%S"
            date = datetime.datetime.now().strftime(format)
            code = code.replace("${date}", date)
            author = getpass.getuser()
            code = code.replace("${author}", author)
            # save
            helper.writeFile(filePath, code)
            v=sublime.active_window().open_file(filePath)
            # cursor
            v.run_command("insert_snippet",{"contents":code})
            sublime.status_message("Js file create success!")

    def is_enabled(self, dirs):
        return len(dirs) == 1


class QuickxjsRebuildUserDefinitionCommand(sublime_plugin.WindowCommand):
    def __init__(self,window):
        super(QuickxjsRebuildUserDefinitionCommand,self).__init__(window)
        self.lastTime=0

    def run(self, dirs):
        curTime=time.time()
        if curTime-self.lastTime<3:
            sublime.status_message("Rebuild frequently!")
            return
        self.lastTime=curTime
        if not os.path.exists(TEMP_PATH):
            os.makedirs(TEMP_PATH)

        rebuild.rebuildsnippets(dirs[0],TEMP_PATH)
        sublime.status_message("Rebuild user definition complete!")
    
    def is_enabled(self, dirs):
        return len(dirs)==1

    def is_visible(self, dirs):
        return self.is_enabled(dirs)

# build file definition when save file
class QuickxJsListener(sublime_plugin.EventListener):
    def __init__(self):
        self.lastTime=0

    def on_post_save(self, view):
        filename=view.file_name()
        if not filename:
            return
        if not helper.checkFileExt(filename,"js"):
            return
        # rebuild user definition
        curTime=time.time()
        if curTime-self.lastTime<2:
            return
        self.lastTime=curTime

        if not os.path.exists(TEMP_PATH):
            os.makedirs(TEMP_PATH)
        rebuild.rebuildSingle(filename,TEMP_PATH)

        sublime.status_message("Current file definition rebuild complete!")

# st3
def plugin_loaded():
    sublime.set_timeout(init, 200)

# st2
if not helper.isST3():
    init()

