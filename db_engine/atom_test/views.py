from django.shortcuts import render

# Create your views here.
from atom_act.models import AtomAct
from atom_learn.algorithms import ALGORITHM_PARAMS
from atom_learn.models import AtomLearn, AtomLearnParam
from atom_test.models import AtomTest
from comm_model.apps import COMPONENTS
from comm_model.components.AtomCommon import extract_component_type
from csv_reader.apps import FieldType
from csv_reader.csv_reader import check_target
from csv_reader.models import CsvReaderInfo, CsvReaderInfotype
from common import ERRORS
from common.UTIL import auto_param, Response
import copy

@auto_param()
def save(request, project_id, component_id, atom_act_id, input_comp_id, feature_id, feature_target):
    if feature_target == "" or feature_id == "":
        return Response.fail(ERRORS.PARAMS_NOT_IS_NULL)
    if check_target(project_id, input_comp_id, feature_target):
        return Response.fail(ERRORS.TARGET_FIELD_SELECT_ERROR)
    atom_acts = AtomAct.objects.filter(
        project_id=project_id,component_id=atom_act_id
    )
    if len(atom_acts) == 0:
        return Response.fail(ERRORS.ATOM_ACT_NOT_CONFIGURED, None)
    atom_act = atom_acts[0]
    assert isinstance(atom_act, AtomAct)

    # learn_input_type = extract_component_type(atom_act.input_comp_id)
    # test_input_type = extract_component_type(input_comp_id)
    # feature_id = atom_act.feature_id
    # feature_target = atom_act.feature_target

    csv_readers = CsvReaderInfo.objects.filter(
        project_id=project_id, component_id=input_comp_id
    )
    if len(csv_readers) == 0:
        return Response.fail(ERRORS.COMPONENT_NOT_EXIST, None)
    csv_reader = csv_readers[0]
    assert isinstance(csv_reader, CsvReaderInfo)

    AtomTest.objects.filter(project_id=project_id, component_id=component_id).delete()
    AtomTest(project_id=project_id, component_id=component_id, atom_act_id=atom_act_id,
             input_comp_id=input_comp_id,feature_id=feature_id,feature_target=feature_target).save()
    return Response.success('')

@auto_param()
def load(request, project_id, component_id, atom_act_id, input_comp_id):
    fields = list()
    csv_input_type = extract_component_type(input_comp_id)
    if csv_input_type == COMPONENTS.CSV_READER:
        fields = CsvReaderInfotype.objects.filter(project_id=project_id, component_id=input_comp_id)
    else:
        return Response.fail(ERRORS.CSV_TYPE_ERROR, None)

    atom_test_db = AtomTest.objects.filter(project_id=project_id, component_id=component_id)
    if len(atom_test_db) == 0:
        return Response.success()
        # return Response.fail(ERRORS.ATOM_TEST_NOT_CONFIGURED, None)

    data_changed = Response.success("changed")
    atom_test = atom_test_db[0]
    params = list()
    for db_field_type in fields:
        # params.append({"field":field,"field_type":field_type,"date_format":date_format,"sample_data":sample_data})
        params.append( FieldType(db_field_type.field,
                                 db_field_type.selected,
                                 db_field_type.field_type,
                                 db_field_type.date_format,
                                 db_field_type.sample_data))

        # 检查 input_comp_id 是否一样
        if atom_test.input_comp_id != input_comp_id:
            atom_test_db.delete()
            return data_changed
        # todo 检查 id， target 是否在其中，还缺少 robotx和自定义特征组合
        # 检查通过，返回需要初始化的内容
        result = dict(
            id=atom_test.feature_id,
            target=atom_test.feature_target,
            # max_value=atom_test.max_value,
            fields=params
        )
        return Response.success(result)
