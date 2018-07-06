from django.shortcuts import render

from collections import OrderedDict

# from atom_learn.algorithms import ALGORITHM_PARAMS
from comm_model.apps import COMPONENTS
from comm_model.components.AtomCommon import param_checking
from comm_model.components.Component import Param, ParamCheckingError
from common.UTIL import auto_param, mk_working_directory, Response, is_date
from csv_reader.models import CsvReaderInfotype
from . import algorithms
from common import ERRORS
from .models import AtomLearn,AtomLearnParam
from typing import List
import copy
# Create your views here.
def __orderd_dict__(params):
    odt = OrderedDict()
    for param in params:
        odt[param['name']] = param
    return odt

ALGORITHM_PARAMS = {
    algorithm: __orderd_dict__(params)
    for algorithm, params in algorithms.ALGORITHM_PARAMS.items()
}

container_query_sql_lst = [
    "select a.*",
    "from csv_reader_infotype a",
    "	INNER JOIN container b on a.project_id = b.project_id and a.component_id = b.container_id",
    "where a.project_id = '{project_id}'",
    "	and b.component_id = '{component_id}'"
]
container_fields_sql_lst = [
    "select a.*",
    "from io_field_type a",
    "	INNER JOIN container b on a.project_id = b.project_id and a.component_id = b.container_id",
    "	INNER JOIN featurecombine c on b.project_id = c.project_id and b.component_id = c.robotx_spark_id",
    "where a.project_id = '{project_id}'",
    "	and c.component_id = '{component_id}'"
]

field_in_sql = "and a.field in ('{id}','{target}')"
robotx_field_in_query = "\n".join(container_query_sql_lst + [field_in_sql])
combine_field_in_query = "\n".join(container_fields_sql_lst + [field_in_sql])

# view 请求
@auto_param()
def load_list(request):
    return Response.success(algorithms.ALGORITHMS)

@auto_param()
def load_list_params(request, name):
    if name not in algorithms.ALGORITHM_PARAMS:
        return Response.fail(ERRORS.ALGORITHM_NOT_SUPPORTED, None)
    return Response.success(algorithms.ALGORITHM_PARAMS[name])

# 保存默认值
@auto_param()
def save_with_default(request, project_id, atom_learn_id, input_comp_id, algorithm):
    """
    保存，算法的高级参数使用默认
    :param request:
    :param project_id:
    :param atom_learn_id:
    :param input_comp_id:
    :param algorithm:
    :return:
    """
    try:
        if algorithm not in algorithms.ALGORITHM_PARAMS:
            return Response.fail(ERRORS.ALGORITHM_NOT_SUPPORTED, None)
        AtomLearn.objects.update_or_create(
            project_id=project_id, component_id=atom_learn_id,
            defaults=dict(
                input_comp_id=input_comp_id, algorithm=algorithm))
        params = list()
        if algorithm not in ["naivebayes","lr"]:
            default_params = ALGORITHM_PARAMS[algorithm]
            for param in default_params:
                params.append(AtomLearnParam(project_id=project_id, component_id=atom_learn_id, param_name=param,
                                             param_value=str(default_params[param]['default'])))
        AtomLearnParam.objects.filter(project_id=project_id, component_id=atom_learn_id).delete()
        AtomLearnParam.objects.bulk_create(params)
        result = {"data": "保存成功", "status": True, "error": ""}
        return Response.success(result)
    except UnicodeDecodeError as e:
        response = Response.fail(ERRORS.SAVE_PARAM_ERROR, None)
        return response


# 修改保存
@auto_param()
def saveInfo(request, project_id, atom_learn_id, input_comp_id, algorithm, params: List[Param]):
    # __ALGORITHM_PARAMS = ALGORITHM_PARAMS
    if algorithm not in ALGORITHM_PARAMS:
        return Response.fail(ERRORS.ALGORITHM_NOT_SUPPORTED, None)
    algorithm_params = ALGORITHM_PARAMS[algorithm]
    db_params = list()
    checking_results = list()
    for param in params:
        values = param.values
        param_name = param.name
        # 参数检查
        param_limit = algorithm_params[param_name]
        checking_result = param_checking(param_name, values, param_limit)
        if checking_result is not None:
            checking_results.append(checking_result)
        else:
            db_params.append(AtomLearnParam(project_id=project_id, component_id=atom_learn_id, param_name=param_name,
                                         param_value=values))
    # 参数有错
    if len(checking_results) > 0:
        return Response.fail(ERRORS.ALGORITHM_PARAM_ERROR, checking_results)
    AtomLearn.objects.update_or_create(
        project_id=project_id, component_id=atom_learn_id,
        defaults=dict(
            input_comp_id=input_comp_id, algorithm=algorithm))
    AtomLearnParam.objects.filter(project_id=project_id, component_id=atom_learn_id).delete()
    AtomLearnParam.objects.bulk_create(db_params)
    result = {"data": "保存成功", "status": True, "error": ""}
    return Response.success(result)


@auto_param()
def load(request, project_id, atom_learn_id,input_comp_id):
    atom_learn_db = AtomLearn.objects.filter(project_id=project_id, component_id=atom_learn_id)
    if len(atom_learn_db) == 0:
        # 刚新建组件
        return Response.success()
    data_changed = Response.success("changed")
    atom_learn = atom_learn_db[0]
    # 检查 input_comp_id 是否一样
    if atom_learn.input_comp_id != input_comp_id:
        atom_learn_db.delete()
        return data_changed
    # todo 检查 id， target 是否在其中，还缺少 robotx和自定义特征组合
    fields = list()
    if input_comp_id.startswith(COMPONENTS.CSV_READER):
        fields = CsvReaderInfotype.objects.filter(project_id=project_id, component_id=input_comp_id)
            # ,field__in=[atom_learn.feature_id, atom_learn.feature_target])
    elif input_comp_id.startswith(COMPONENTS.ROBOTX):
        # RobotX
        fields = list(CsvReaderInfotype.objects.raw(robotx_field_in_query.format(
            project_id=project_id,
            component_id=input_comp_id,
            id=atom_learn.feature_id,
            target=atom_learn.feature_target
        )))
    elif input_comp_id.startswith(COMPONENTS.ATOM_EXPLORE):
        fields = AtomLearnParam.objects.filter(project_id=project_id, component_id=atom_learn_id)

    # id target 不在字段中
    # if len(fields) == 0:
    #     atom_learn_db.delete()
    #     return data_changed

    # 检查通过，返回需要初始化的内容
    algorithm_params = ALGORITHM_PARAMS[atom_learn.algorithm]
    atom_learn_params = AtomLearnParam.objects.filter(project_id=project_id, component_id=atom_learn_id)
    params = list()
    for atom_learn_param in atom_learn_params:
        if atom_learn_param.param_name in algorithm_params:
            algorithm_param = copy.copy(algorithm_params[atom_learn_param.param_name])
            algorithm_param['value'] = atom_learn_param.param_value
            params.append(algorithm_param)

    result = dict(
        # id=atom_learn.feature_id,
        # target=atom_learn.feature_target,
        algorithm=atom_learn.algorithm,
        params=params
    )
    
    return Response.success(result)
