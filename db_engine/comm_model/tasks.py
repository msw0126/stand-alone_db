import datetime
import logging
import os
import subprocess
from functools import wraps
from urllib import parse

from django.db.models import F
from lxml import etree

import requests
from celery import shared_task
from django.db import connections
from py4j.java_gateway import JavaGateway

import setting
from comm_model import apps
from comm_model.apps import FAILED, SUCCEEDED
from comm_model.components.AtomCommon import extract_component_type
from comm_model.components.Component import Component
from comm_model.models import Task, Execution, TaskRelies
from common import ERRORS
from common.UTIL import Response
from setting import WORKING_DIRECTORY, ATOM_PATH,COMPONENT_DIR
from . import LogQuery
import time


def config_resource(project_id, component_id):
    # yarn_model = YarnResourceModel.objects.filter(project_id=project_id, component_id=component_id)
    saving_path = os.path.join(WORKING_DIRECTORY, project_id, component_id)
    if not os.path.exists(saving_path) or not os.path.isdir(saving_path):
        raise Exception("文件夹路径不存在")
    return saving_path


def common_setting(project_id, component_id):
    # common_env_setting()
    # saving_path = os.path.join(WORKING_DIRECTORY, project_id, component_id)
    # resource = config_resource(project_id, component_id)
    # command = [resource]
    command = setting.ATOM_PATH
    return command

def connection_check():
    for conn in connections.all():
        if conn.connection is not None:
            conn.is_usable()

def task_recorder(func):
    @wraps(func)
    def wrapper(*arg, **kwargs):
        project_id = kwargs['project_id']
        component_id = kwargs['component_id']
        task_id = kwargs['task_id']
        start_time = datetime.datetime.now()
        # 更新状态为运行
        connection_check()
        Task.objects.filter(project_id=project_id, component_id=component_id).update(start_time=start_time,
                                                                                     task_status=apps.RUNNING)
        res = func(*arg, **kwargs)
        end_time = datetime.datetime.now()
        connection_check()
        Task.objects.filter(project_id=project_id, component_id=component_id).update(end_time=end_time, task_status=res)

        if res == apps.SUCCEEDED:
            task_count = Execution.objects.filter(project_id=project_id, task_id=task_id)[0].task_count
            task_success_count = Task.objects.filter(project_id=project_id, task_id=task_id, task_status=apps.SUCCEEDED).count()
            if task_success_count==task_count:
                Execution.objects.filter(project_id=project_id, task_id=task_id).update(
                    status=apps.ExecutionStatus.SUCCEEDED, end_time=end_time)
            else:
                # 更新其他组件依赖状态
                forwards = TaskRelies.objects.filter(project_id=project_id, sc_comp_id=component_id)
                forwards = [forward.tg_comp_id for forward in forwards]
                Task.objects.filter(project_id=project_id, component_id__in=forwards).update(relies=F('relies') - 1)
        else:
            Execution.objects.filter(project_id=project_id, task_id=task_id).update(
                status=apps.ExecutionStatus.FAILED, end_time=end_time)
        return res
    return wrapper

def update_task_detail(project_id, component_id, task_id, error_code=None, detail=None):
    update_dict = dict()
    if error_code is not None:
        update_dict['error_code'] = error_code
    if detail is not None:
        update_dict['detail'] = detail
    if len(update_dict) ==0 :
        return
    connection_check()
    print("==================",update_dict['detail'])
    Task.objects.filter(project_id= project_id, component_id= component_id, task_id=task_id).update(**update_dict)

def local_submit(project_id, component_id, task_id, p):
    error_code = None
    submit_log = list()

    # status = apps.SUCCEEDED
    # error = p.stderr.readline().strip()
    #
    # if len(error) != 0:
    #     status = apps.FAILED
    #
    # for line in iter(p.stdout.readline, b''):
    #     # while p.poll() is None:
    #     submit_log.append(str(line))
    # p.stdout.close()
    # for line in iter(p.stderr.readline, b''):
    #     submit_log.append(str(line))
    # p.stderr.close()

    while p.poll() is None:
        line = p.stdout.readline()
        line = line.decode('utf-8', 'ignore').strip()
        submit_log.append(line)
        line = p.stderr.readline()
        line = line.decode('utf-8', 'ignore').strip()
        submit_log.append(line)
        if len(line) > 0 and "Error" in line:
            error_code = apps.FAILED
    print(p.returncode)
    if error_code == None and p.returncode == 0:
        error_code = apps.SUCCEEDED
    else:
        error_code = apps.FAILED
    while '' in submit_log:
        submit_log.remove('')
    update_task_detail(project_id, component_id, task_id, error_code=error_code, detail="\\n".join(submit_log))
    return error_code

def printP(project_id, component_id, task_id,p):
    error_line = list()
    error_code = None
    while p.poll() is None:
        line = p.stderr.readline()
        print(line)
        line = line.decode('utf-8', 'ignore').strip()
        if len(error_line) != 0:
            if len(line) > 0: error_line.append(line)
            continue
        elif len(line) > 0 :
            error_code = ERRORS.TASK_HAS_NO_LOG
            error_line.append(line)
            continue
    p.kill()

    if error_code is not None:
        # 任务提交时发生错误
        update_task_detail(project_id, component_id, task_id, error_code=error_code, detail="<br />".join(error_line))
        return apps.FAILED
# ======================================================
# task功能
#=======================================================

@shared_task
@task_recorder
def atom_explore_execute(project_id, component_id, task_id):
    from comm_model.components.AtomExplore import AtomExplore

    partial_command = common_setting(project_id, component_id)
    partial_config = AtomExplore.get_config_path(project_id, component_id)
    command = partial_command , "Explore" , "-conf" , partial_config
    print(" ".join(command))
    status = None
    try:
        p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = local_submit(project_id, component_id, task_id, p)
    except Exception as e:
        update_task_detail(project_id, component_id, task_id, detail=str(e))
        return FAILED
    if status != SUCCEEDED:
        return status
    return status


@shared_task
@task_recorder
def atom_learn_execute(project_id, component_id, task_id):
    from comm_model.components.AtomLearn import AtomLearn
    # config_file_path = AtomLearn.get_config_path(project_id, component_id)
    # hive_reader_dict_path = AtomLearn.hive_reader_dict_path(project_id, component_id)
    # has_local_dict = os.path.exists(hive_reader_dict_path)

    partial_command = common_setting(project_id, component_id)
    partial_config = AtomLearn.get_config_path(project_id, component_id)
    command = partial_command , "Learn" , "-conf" , partial_config
    print(" ".join(command))
    status = None
    try:
        # p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=COMPONENT_DIR)
        p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = local_submit(project_id, component_id, task_id, p)
    except Exception as e:
        update_task_detail(project_id, component_id, task_id, detail=str(e))
        return FAILED
    if status != SUCCEEDED:
        return status
    return status



@shared_task
@task_recorder
def atom_act_execute(project_id, component_id, task_id):
    from comm_model.components.AtomAct import AtomAct

    config_file_path = AtomAct.get_config_path(project_id, component_id)
    partial_command = common_setting(project_id, component_id)
    command = partial_command , "Act", "-conf",config_file_path
              # + [
              #  "--files", config_file_path,
              #  "--py-files", setting.SPARK_ATOM_PY_FILES,
              #  setting.SPARK_ATOM_RUN, "Act"
              #  ]
    print(" ".join(command))
    status = None
    try:
        p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=setting.COMPONENT_DIR)
        status = local_submit(project_id, component_id, task_id, p)
    except Exception as e:
        update_task_detail(project_id, component_id, task_id, detail=str(e))
        return apps.FAILED

    if status != apps.SUCCEEDED:
        return status

    # bin_local = AtomAct.get_prediction_bin_local_path(project_id, component_id)
    # bin_hdfs = AtomAct.get_prediction_bin_hdfs_path(project_id, component_id)
    # csv_local = AtomAct.get_prediction_csv_local_path(project_id, component_id)
    # csv_hdfs = AtomAct.get_prediction_csv_hdfs_path(project_id, component_id)
    #
    # try:
    #     download_report([bin_hdfs, csv_hdfs], [bin_local, csv_local])
    #     AtomAct.generate_report(project_id, component_id)
    # except Exception as e:
    #     update_task_detail(project_id, component_id, task_id, error_code="REPORT_GENERATE_ERROR")
    #     return apps.FAILED

    return status

@shared_task
@task_recorder
def atom_test_execute(project_id, component_id, task_id):
    from comm_model.components.AtomTest import AtomTest

    config_file_path = AtomTest.get_config_path(project_id, component_id)

    partial_command = common_setting(project_id, component_id)
    command = partial_command , "Test", "-conf",config_file_path
    print(" ".join(command))
    status = None
    try:
        p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=setting.COMPONENT_DIR)
        status = local_submit(project_id, component_id, task_id, p)
    except Exception as e:
        update_task_detail(project_id, component_id, task_id, detail=str(e))
        return apps.FAILED
    # status = spark_submit(project_id, component_id, task_id, p)

    if status != apps.SUCCEEDED:
        return status

    # metric_local = AtomTest.get_test_metrics_local_path(project_id, component_id)
    # metric_hdfs = AtomTest.get_test_metrics_hdfs_path(project_id, component_id)
    #
    # try:
    #     download_report([metric_hdfs], [metric_local])
    #     AtomTest.generate_report(project_id, component_id)
    # except Exception as e:
    #     update_task_detail(project_id, component_id, task_id, error_code="REPORT_GENERATE_ERROR")
    #     return apps.FAILED
    return status


@shared_task
@task_recorder
def feature_combine_execute(project_id, component_id, task_id):
    from comm_model.components.FeatureCombine import FeatureCombine
    from comm_model.components.SelfDefinedFeature import SelfDefinedFeature
    from comm_model.models import FeatureCombine as FeatureCombineModel

    feature_combines = FeatureCombineModel.objects.filter(project_id=project_id, component_id=component_id)
    feature_combine = feature_combines[0]
    connected_self_feature = feature_combine.self_defined_feature_id
    self_defined_csv_file = SelfDefinedFeature.csv_file_path(project_id, connected_self_feature)
    config_file_path = FeatureCombine.get_config_path(project_id, component_id)

    partial_command = common_setting(project_id, component_id)
    command = partial_command
    print(" ".join(command))
    status = None
    try:
        p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=setting.COMPONENT_DIR)
        status = local_submit(project_id, component_id, task_id, p)
    except Exception as e:
        update_task_detail(project_id, component_id, task_id, detail=str(e))
        return apps.FAILED
    return status


@shared_task
@task_recorder
def robotx_execute(project_id, component_id, task_id):
    # 初始化 RobotxSpark类
    from comm_model.components.RobotX import RobotX
    component_type = extract_component_type(component_id)
    robotx_class = eval(component_type)
    robotx_obj = robotx_class(project_id, component_id)
    # robotx 输出
    output_path, output_dict = robotx_obj.output

    config_file_path = robotx_obj.get_config_path
    partial_command = setting.ROBOTX_PATH
    command = partial_command ,\
                                 "--config_path", config_file_path,\
                                 "--output", output_dict,\
                                 "--dict_only n",\
                                 "--dbname testdb_%s_%s_%s"%(project_id,component_id,task_id),\
                                 "--delete_db y",\
                                 "--label ","robot_x"

    print(" ".join(command))
    status = apps.SUCCEEDED
    try:
        p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        submit_log = list()
        # while p.poll() is None:
        #     out = p.stdout.readline().decode('utf-8', 'ignore').strip()
        #     error = p.stderr.readline().decode('utf-8', 'ignore').strip()
        #     submit_log.append(out)
        #     if len(error) > 0 :
        #         status = apps.FAILED
        #         submit_log.append(error)

        error = p.stderr.readline().strip()

        if len(error) != 0:
            status = apps.FAILED

        for line in iter(p.stdout.readline, b''):
            # while p.poll() is None:
            submit_log.append(str(line))
        p.stdout.close()
        for line in iter(p.stderr.readline, b''):
            submit_log.append(str(line))
        p.stderr.close()


        update_task_detail(project_id, component_id, task_id, error_code="", detail="\\n".join(submit_log))
    except Exception as e:
        update_task_detail(project_id, component_id, task_id, detail=str(e))
        return apps.FAILED
    return status
