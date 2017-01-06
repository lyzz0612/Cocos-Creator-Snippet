#coding=utf8
import os
import shutil
import re
#替换正则
#    /\*[\w\W]*?\*/
#    \n[\t ]*\n
#     : .*?([,\);]) $1


def writeToFile(folderName, fileName, text, trigger, desc):
    global output_path
    folderName = folderName.strip()
    fileName = fileName.strip()
    if folderName == "" or fileName == "":
        return

    if not os.path.exists(output_path + folderName):
        os.mkdir(output_path + folderName)
    writeObj = open(output_path + folderName + "/" + fileName + ".sublime-snippet", "w")
    writeObj.write("<snippet>\n\t<content><![CDATA[")
    writeObj.write(text)
    writeObj.write("]]></content>\n\t<tabTrigger>")
    writeObj.write(trigger)
    writeObj.write("</tabTrigger>\n\t<scope>source.js</scope>\n\t<description>")
    writeObj.write(desc)
    writeObj.write("</description>\n</snippet>")
    writeObj.close()

def dealWithModuleFunc(funcVal, moduleName):
    match = re.match("(.*?)\((.*)\)", funcVal)
    if match:
        funcName = match.group(1)
        paramText = match.group(2)
        if "(" in paramText:
            return
        
        paramList = paramText.split(",")
        text = funcName + "("
        triggerText = text
        for i in range(0, len(paramList)):
            param = paramList[i]
            if param == "":
                break
            param = param.split(":")[0].strip()
            text = "%s${%d:%s}" %(text, i+1, param.strip())
            triggerText = triggerText + param
            
            if (i+1) != len(paramList):
                text = text + ", "
                triggerText = triggerText + ", "
        text = text + ")"
        triggerText = triggerText + ")"
        writeToFile(moduleName, funcName, text, triggerText, moduleName)

def dealWithClass(funcVal, className):
    match = re.match("(.*)\((.*)\)", funcVal)
    if match:
        funcName = match.group(1)
        paramText = match.group(2)
        paramList = paramText.split(",")
        text = funcName + "("
        for i in range(0, len(paramList)):
            param = paramList[i]
            text = "%s${%d:%s}" %(text, i+1, param.strip())
            if (i+1) != len(paramList):
                text = text + ", "
        text = text + ")"    
        writeToFile(className, funcName, text, funcVal, className)
    else:
        writeToFile(className, funcVal, funcVal, className+"."+funcVal, className)

api_path = ""
output_path = ""

def main():
    global api_path, output_path
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.mkdir(output_path)
    
    fileObj = open(api_path, "r")
    moduleName = ""
    enumName = ""
    className = ""
    innerModule = ""

    for line in fileObj:
        match = re.match("declare module (.*) {", line)
        if match:
            moduleName = match.group(1)
            continue
            
        match = re.match("\texport function (.*) :", line)
        if match:
            dealWithModuleFunc(match.group(1), moduleName)
            continue
            
        match = re.match("\texport var (.*?) ", line)
        if match:
            varName = match.group(1)
            writeToFile(moduleName, varName, moduleName+"."+varName, moduleName+"."+varName, moduleName)
            continue

        match = re.match("\t+}", line)
        if match:
            if enumName:
                enumName = None
            elif className:
                className = None
            elif innerModule:
                innerModule = None
            continue
            
        match = re.match("\texport module (.*) {", line)
        if match:
            innerModule = match.group(1)
            writeToFile(moduleName, innerModule, moduleName+"."+innerModule, moduleName+"."+innerModule, moduleName)
            continue
        
        match = re.match("\t+export enum (.*) {", line)
        if match:
            enumName = match.group(1)
            parent = innerModule or className or moduleName
            writeToFile(parent, enumName, parent+"."+enumName, parent+"."+enumName, parent)
            continue
        #enum值
        match = re.match("\t+(.*) = .*,", line)
        if match and enumName:
            if enumName == "KEY": 
                continue
            itemName = match.group(1).strip()
            writeToFile(enumName, itemName, enumName+"."+itemName, enumName+"."+itemName, enumName)
            continue
            
        match = re.match("\t+export class (.*?) ", line)
        if match:
            className = match.group(1)
            parent = innerModule or moduleName
            if not className.startswith("_"):
                writeToFile(parent, className, parent+"."+className, parent+"."+className, parent)
            continue
        
        if className and className != "":
            #类成员变量
            match = re.match("\t+([^\(]+) :", line)
            if match:
                varName = match.group(1)
                writeToFile(className, varName, varName, className+"."+varName, className)
                continue
            #类成员函数
            match = re.match("\t+(.*) :", line)
            if match:
                dealWithModuleFunc(match.group(1), className)
                continue
            

if __name__ == "__main__":
    api_path = raw_input("请输入creator.d.ts的路径：")
    output_path = raw_input("请输入snippet输出目录：")

main()