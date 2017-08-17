#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: lonewolf
# Date: 2013-11-11 23:08:52
# 
import sublime
import os
import re
import codecs
if sublime.version()[0] == '2':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

try:
    import helper
except ImportError:
    from . import helper

snippetTemplate = """<snippet>
    <content><![CDATA[$content]]></content>
    <tabTrigger>$trigger</tabTrigger>
    <scope>source.js</scope>
    <description>$desc</description>
</snippet>
"""

# auto completions path: SAVE_DIR/md5(filePath)/...
SAVE_DIR=""

def rebuildsnippets(dir,saveDir):
    global SAVE_DIR
    SAVE_DIR=saveDir
    # delete files first
    deleteFiles(saveDir,saveDir)
    parseDir(dir)

def rebuildSingle(file,saveDir):	
    global SAVE_DIR
    SAVE_DIR=saveDir
    parseJs(file)

def parseDir(dir):
    for item in os.listdir(dir):
        path=os.path.join(dir,item)
        if os.path.isdir(path):
            parseDir(path)
        elif os.path.isfile(path):
            if helper.checkFileExt(path,"js"):
                parseJs(path)

def parseJs(file):
    # remove all file
    md5filename=helper.md5(file)
    saveDir=os.path.join(SAVE_DIR,md5filename)
    deleteFiles(saveDir,saveDir)
    # create dir
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)

    filepath=os.path.join(saveDir,"filepath.txt")
    helper.writeFile(filepath,file)

    end_index = file.rfind("/")
    className = file[end_index+1:-3]

    completionsList=[]
    with open(file, "r", encoding='utf-8') as f:
        for line in f:
            #sample: onLoad: function () {
            m = re.match(' +(\w+): *function *\((.*?)\).*', line)
            if m:
                saveFunction(saveDir, className, m.group(1), m.group(2))
                continue
            #sample: ComFun.dump = function(arr, maxLevel) {
            m = re.match(' *([a-zA-Z0-9\.]*) = function *\((.*?)\).*', line)
            if m:
                saveFunction(saveDir, className, m.group(1), m.group(2))
                continue
            #sample var Constant = {}
            m = re.match('^var (.*) *=.*', line)
            if m:
                completionsList.append(m.group(1).strip())
                continue
            #sample Constant.Enums = something
            m = re.match('^([\w\.]*) *=.*', line)
            if m:
                completionsList.append(m.group(1).strip())
                

    if "module.exports" in completionsList:
        completionsList.remove("module.exports")
    saveCompletions(completionsList,saveDir,"c")
    
def saveFunction(saveDir,classname,function,param): 
    if function == "ctor" or function == "module.exports":
        return
    arr=handleParam(param)
    content=function+"(%s)"%(arr[1])
    trigger=function+"(%s)"%(arr[0])
    template=snippetTemplate.replace("$content",content)
    template=template.replace("$trigger",trigger)
    template=template.replace("$desc",classname)
    a=""
    if arr[0]!="":
        args=arr[0].split(",")
        for i in range(0,len(args)):
            args[i]=re.sub("\W","",args[i])
        a="-".join(args)
        a="-"+a
    saveName=function+a+".sublime-snippet"
    savePath=os.path.join(saveDir,saveName)
    f=open(savePath, "w+")
    f.write(template)
    f.close()

def handleParam(param):
    args=[]
    for item in param.split(","):
        str1=re.sub("\s","",item)
        if str1!="" and str1!="void":
            args.append(str1)
    args2=[]
    for i in range(0,len(args)):
        args2.append("${%d:%s}"%(i+1,args[i]))
    a1=", ".join(args)
    a2=", ".join(args2)
    return [a1,a2]

def saveCompletions(completionsList,saveDir,filename):    
    if len(completionsList)>0:        
        # remove duplicate
        completionsList=sorted(set(completionsList),key=completionsList.index)
        for item in completionsList:
            template=snippetTemplate.replace("$content",item)
            template=template.replace("$trigger",item)
            template=template.replace("$desc",".")
            name=re.sub("\W","_",item)
            saveName=name+".sublime-snippet"
            savePath=os.path.join(saveDir,saveName)
            f=open(savePath, "w+")
            f.write(template)
            f.close()

# delete files under dir
def deleteFiles(path,root):
    if not os.path.exists(path):
        return
    if os.path.isfile(path):
        try:
            os.remove(path)
        except Exception:
            pass
    elif os.path.isdir(path):
        for item in os.listdir(path):
            itemsrc=os.path.join(path,item)
            deleteFiles(itemsrc,root)
        if path!=root:            
            try:
                os.rmdir(path)
            except Exception:
                pass
