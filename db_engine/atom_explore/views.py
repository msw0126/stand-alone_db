import copy
from collections import OrderedDict

from django.shortcuts import render
from typing import List
# Create your views here
import setting
from atom_explore.models import AtomExplore, AtomExploreParam
from comm_model.apps import COMPONENTS
from comm_model.components.AtomCommon import param_checking
from comm_model.components.Component import Param
from common import ERRORS
from common.UTIL import auto_param, Response
from csv_reader.csv_reader import check_target
from csv_reader.models import CsvReaderInfo,CsvReaderInfotype

# 公共方法
def __orderd_dict__(params):
    odt = OrderedDict()
    for param in params:
        odt[param['name']] = param
    return odt

# 公共参数


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

COMM_PARAMS = {
    params['name'] : params
    for params in setting.EXPLORE_COMMON_PARAMS
}
COMM_PARAMS_LIST = set(COMM_PARAMS)


# url请求接口
@auto_param()
def load_list(request):
    return Response.success(setting.EXPLORE_COMMON_PARAMS)

@auto_param()
def load(request, project_id, atom_explore_id, input_comp_id):
    atom_explore_db = AtomExplore.objects.filter(project_id=project_id, component_id=atom_explore_id)
    if len(atom_explore_db) == 0:
        # 刚新建组件
        return Response.success()
    data_changed = Response.success("changed")
    atom_explore = atom_explore_db[0]
    # 检查 input_comp_id 是否一样
    if atom_explore.input_comp_id != input_comp_id:
        atom_explore_db.delete()
        return data_changed
    # todo 检查 id， target 是否在其中，还缺少 robotx和自定义特征组合
    fields = list()
    if input_comp_id.startswith(COMPONENTS.CSV_READER):
        fields = CsvReaderInfotype.objects.filter(project_id=project_id, component_id=input_comp_id,
                                                  field__in=[atom_explore.feature_id, atom_explore.feature_target])
        # ,field__in=[atom_explore.feature_id, atom_explore.feature_target])
    elif input_comp_id.startswith(COMPONENTS.ROBOTX):
        # RobotX
        fields = list(CsvReaderInfotype.objects.raw(robotx_field_in_query.format(
            project_id=project_id,
            component_id=input_comp_id,
            id=atom_explore.feature_id,
            target=atom_explore.feature_target
        )))
    # id target 不在字段中
    if len(fields) != 2:
        atom_explore_db.delete()
        return data_changed

    # 检查通过，返回需要初始化的内容
    atom_explore_params = AtomExploreParam.objects.filter(project_id=project_id, component_id=atom_explore_id)
    params = list()
    for atom_explore_param in atom_explore_params:
        # if atom_explore_param.param_name in COMM_PARAMS_LIST:
        algorithm_param = copy.copy(COMM_PARAMS[atom_explore_param.param_name])
        algorithm_param['value'] = atom_explore_param.param_value
        params.append(algorithm_param)
    result = dict(
        id=atom_explore.feature_id,
        target=atom_explore.feature_target,
        params=params
    )
    return Response.success(result)


@auto_param()
def saveInfo(request, project_id, atom_explore_id, input_comp_id, id, target, params: List[Param]):
    # __COMM_PARAMS = COMM_PARAMS
    # if target != "Target":
    #     return Response.fail(ERRORS.TARGET_FIELD_SELECT_ERROR)

    if check_target(project_id, input_comp_id,target):
        return Response.fail(ERRORS.TARGET_FIELD_SELECT_ERROR)

    params_list = set([param_.name for param_ in params])
    for name in params_list:
        if name not in COMM_PARAMS:
            return Response.fail(ERRORS.EXPLORE_PARAM_ERROR, None)
    db_params = list()
    checking_results = list()
    for param in params:
        values = param.values
        param_name = param.name
        # 参数检查
        param_limit = COMM_PARAMS[param_name]
        checking_result = param_checking(param_name, values, param_limit)
        if checking_result is not None:
            checking_results.append(checking_result)
        else:
            db_params.append(AtomExploreParam(project_id=project_id, component_id=atom_explore_id, param_name=param_name,
                                         param_value=values))
    # 参数有错
    if len(checking_results) > 0:
        return Response.fail(ERRORS.EXPLORE_PARAM_ERROR, checking_results)
    AtomExplore.objects.update_or_create(
        project_id=project_id, component_id=atom_explore_id,
        defaults=dict(
            input_comp_id=input_comp_id, feature_id=id, feature_target=target))
    AtomExploreParam.objects.filter(project_id=project_id, component_id=atom_explore_id).delete()
    AtomExploreParam.objects.bulk_create(db_params)
    result = {"data": "保存成功", "status": True, "error": ""}
    return Response.success(result)



# 保存默认值
@auto_param()
def saveInfoDefualt(request, project_id, atom_explore_id, input_comp_id, id, target):
    """
    保存，算法的高级参数使用默认
    :param request:
    :param project_id:
    :param atom_explore_id:
    :param input_comp_id:
    :param id:
    :param target:
    :param algorithm:
    :return:
    """
    # csv_reader = CsvReaderInfo.objects.filter(project_id=project_id,component_id=input_comp_id)
    # if len(csv_reader) == 0:
    #     return Response.fail(ERRORS.CSV_READER_NOT_CONFIGURED, None)
    # if target != "Target":
    #     return Response.fail(ERRORS.TARGET_FIELD_SELECT_ERROR)
    if check_target(project_id, input_comp_id,target):
        return Response.fail(ERRORS.TARGET_FIELD_SELECT_ERROR)

    default_params = COMM_PARAMS
    params = list()
    for param in default_params:
        params.append(AtomExploreParam(project_id=project_id, component_id=atom_explore_id, param_name=param,
                                     param_value=str(default_params[param]['default'])))
    AtomExploreParam.objects.filter(project_id=project_id, component_id=atom_explore_id).delete()
    AtomExploreParam.objects.bulk_create(params)
    AtomExplore.objects.update_or_create(
        project_id=project_id, component_id=atom_explore_id,
        defaults=dict(
            input_comp_id=input_comp_id, feature_id=id, feature_target=target))
    result = {"data": "保存成功", "status": True, "error": ""}
    return Response.success(result)
