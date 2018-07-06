# Create your views here.
import codecs
import os

import re

from django.http import StreamingHttpResponse

import setting
from comm_model import apps
from comm_model.components.AtomCommon import extract_component_type
from comm_model.executor import execute, execution_status, current_execution, get_log, kill_task, stop_all, \
    get_id, delete, queryLog
from common.UTIL import Response, auto_param
from common.Zip import ZipUtilities


def _execute(request):
   return execute(request)


def _execution_status(request):
    return execution_status(request)


def _current_execution(request):
    return current_execution(request)


def _get_log(request):
    return get_log(request)

def _kill_task(request):
    return kill_task(request)


def _stop_all(request):
    return stop_all(request)


def _get_id(request):
    return get_id(request)


def _delete(request):
    return delete(request)


def _queryLog(request):
    return queryLog(request)

def getDir(project_id, component_id=None):
    component_type = None
    dir = None
    if component_id != None:
        component_type = extract_component_type(component_id)
        component_type = re.sub('Atom', '', component_type)
    if component_type != None:
        dir = os.path.join(setting.WORKING_DIRECTORY, project_id, component_type)
        # dir = os.path.join(setting.WORKING_DIRECTORY, project_id, component_id, component_type)
    else:
        dir = os.path.join(setting.WORKING_DIRECTORY, project_id)
    return dir

def fileList(project_id, component_id=None):
    fileList = list()
    dir = getDir(project_id, component_id)
    files = os.listdir(dir)
    # for file in files:
    #     fileList.append(file)
    return files

def getDate():
    import datetime
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d%H%M%S')

# def getZipfile(file):
#     pathf = os.path.dirname(file)
#     fileName = file[len(pathf) + 1:]
#     return fileName

@auto_param()
def reportFiles(request, project_id, component_id):
    if project_id == None or project_id == "":
        return Response.fail("工程id参数不能为空")
    return Response.success(fileList(project_id, component_id))

# @auto_param()
def report(request):
    project_id = request.GET.get('project_id')
    component_id = request.GET.get('component_id')
    fileName = request.GET.get('fileName')
    error_msg = "参数缺失"
    if project_id is None or project_id == "":
        return Response.fail(error_msg)
    if component_id is None or component_id == "":
        return Response.fail(error_msg)
    component_type = re.sub('Atom', '', extract_component_type(component_id))
    if fileName is None or fileName == "":
        if component_type in apps.COMPONENTS.ROBOTX:
            fileName = "tmp/full.sql"
        else:
            fileName =component_type+".txt"
    print(setting.WORKING_DIRECTORY, project_id, component_type,fileName)
    file = os.path.join(setting.WORKING_DIRECTORY, project_id, component_type,fileName)
    # file = os.path.join(setting.WORKING_DIRECTORY, project_id, component_id, component_type,fileName)
    try:
        with codecs.open(file, 'r+') as get:
            content = get.read()
    except FileNotFoundError:
        content = "File is not found. or You don't have permission to access this file."
    return Response.success({"data":content})

# @auto_param()
def downLoadReportZip(request):
    project_id = request.GET.get('project_id')
    component_id = request.GET.get('component_id')
    error_msg = "参数缺失"
    if project_id is None or project_id == "":
        return Response.fail(error_msg)
    zipfiles = None
    file_objs = None
    if component_id == "" or component_id == None:
        return Response.fail(error_msg)
        zipfiles = "_".join([project_id,getDate()])
        file_objs = fileList(project_id)
    else:
        zipfiles = "_".join([project_id,component_id,getDate()])
        file_objs = fileList(project_id, component_id)

    dir = getDir(project_id,component_id)
    print(zipfiles)
    utilities = ZipUtilities()
    for file_obj in file_objs:
        tmp_dl_path = os.path.join(dir, file_obj)
        utilities.toZip(tmp_dl_path, zipfiles)
    # utilities.close()
    response = StreamingHttpResponse(utilities.zip_file, content_type='application/zip')
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(zipfiles+".zip")

    return response

