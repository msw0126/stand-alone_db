import csv
import logging
from typing import List

import pandas
from django.http import HttpResponse

from comm_model.components.AtomCommon import extract_component_type
from common import ERRORS
from common.UTIL import auto_param, mk_working_directory, Response
from csv_reader.apps import FieldType
from csv_reader.models import CsvReaderInfo,CsvReaderInfotype

logger = logging.getLogger(__name__)


@auto_param()
def upload(request, project_id, component_id, file):
    # 保存文件
    file_name = file.name
    data_saving_path = mk_working_directory(project_id, component_id, file_name)
    with open(data_saving_path, 'wb') as destination:
        if file.multiple_chunks():
            for chunk in file.chunks():
                destination.write(chunk)
        else:
            destination.write(file.read())
    # 检查文件，判断数据类型
    response = None
    field_types = None  # type: dict[str,FieldType]
    try:
        header = None
        column_num = -1
        with(open(data_saving_path, 'r', encoding='utf-8')) as f:
            csv_reader = csv.reader(f)
            for row_num, row in enumerate(csv_reader):
                # if row_num == 0 and "Target" not in [item.capitalize() for item in row]:
                #     return Response.fail(ERRORS.NO_TARGET_FEILD, None)
                if row_num>21:
                    break
                if header is None:
                    column_num = len(row)
                    if column_num < 2:
                        # csv列数量太少
                        response = Response.fail(ERRORS.CSV_COLUMN_SIZE_ERROR,None)
                        return response
                    header = row
                    field_types = {column : FieldType(column) for column in row}
                else:
                    len_of_column = len(row)
                    if len_of_column!=column_num:
                        response = Response.fail(ERRORS.CSV_COLUMN_NUM_ERROR, dict(
                            header_column_num=column_num,
                            line=row_num+1,
                            row_column_num = len_of_column
                        ))
                        return response
                    for column, sample in zip(header, row):
                        # if column.capitalize() == "Target" and sample not in ["0","1"]:
                        #     return Response.fail(ERRORS.TARGET_FIELD_ERROR, None)
                        field_types[column].add_sample_data(sample)
        if header is None:
            response = Response.fail(ERRORS.CSV_EMPTY, None)
            return response
        if len(field_types[header[0]].sample_data)<20:
            response = Response.fail(ERRORS.CSV_ROW_TOO_SMALL, None)
            return response
        # 数据类型判断
        db_field_types = []
        fields = field_types.values()
        sorted(fields, key=lambda x:x.field)

        for head in header:
            field = field_types[head]
            field.guess_field_type()
        # for field in field_types.values():
        #     field.guess_field_type()
            db_field_types.append(field.to_db_type(project_id, component_id))

        # 保存类型
        CsvReaderInfotype.objects.filter(project_id=project_id, component_id=component_id).delete()
        CsvReaderInfotype.objects.bulk_create(db_field_types)
        response = Response.success(db_field_types)
        # response = Response.success(list(field_types.values()))
        return response
    except UnicodeDecodeError as e:
        response = Response.fail(ERRORS.CSV_UTF8_ERROR, None)
        return response

@auto_param()
def update(request, project_id, component_id, field_types: List[FieldType]):
    # 修改资料
    db_field_types = []
    for field in field_types:
        db_field_types.append(field.to_db_type(project_id, component_id))
    # 检查数据类型
    response = None
    # field_types = None  # type: dict[str,FieldType]
    try:
        # 保存类型
        for db_field_type in db_field_types:
            field = db_field_type.field
            field_type = db_field_type.field_type
            selected =  db_field_type.selected
            date_format =  db_field_type.date_format
            CsvReaderInfotype.objects.filter(project_id=project_id, component_id=component_id,field=field).update(
                field_type=field_type,
                date_format =date_format,
                selected=selected,
            )

        response = Response.success({"status":True,"data":"修改成功","error": None})
        return response
    except UnicodeDecodeError as e:
        response = Response.fail(ERRORS.CSV_UTF8_ERROR, None)
        return response

@auto_param()
def saveInfo(request, project_id, component_id, magic_name,file_name):
    try:
        # 保存组件
        CsvReaderInfo.objects.filter(project_id=project_id,component_id=component_id).delete()
        CsvReaderInfo(project_id=project_id,component_id=component_id,magic_name=magic_name,file_name=file_name).save()
        result = {"data":{},"status":True,"error":""}
        response = Response.success(result)
        return response
    except UnicodeDecodeError as e:
        response = Response.fail(ERRORS.CSV_SAVE_ERROR, None)
        return response


@auto_param
def save_field_type(request, project_id, component_id, field_types: List[FieldType]):
    db_field_types = []
    for field in field_types:
        db_field_types.append(field.to_db_type(project_id, component_id))
    # 保存类型
    # SelfDefinedFeatureType.objects.filter(project_id=project_id, component_id=component_id).delete()
    # SelfDefinedFeatureType.objects.bulk_create(db_field_types)
    response = Response.success()
    return response


@auto_param()
def load_field_type(request, project_id, component_id):
    # objs = CsvReaderInfo.objects.filter(project_id=project_id, component_id=component_id)
    # if len(objs)!=1:
    #     response = Response.fail(ERRORS.COMPONENT_NOT_EXIST, None)
    #     return response
    db_field_types = CsvReaderInfotype.objects.filter(project_id=project_id, component_id=component_id)
    field_types = list()
    for db_field_type in db_field_types:
        field_types.append(FieldType(
            db_field_type.field,
            db_field_type.selected,
            db_field_type.field_type,
            db_field_type.date_format,
            db_field_type.sample_data,
            # field, selected, field_type = None, date_format = None, sample_data = None,
        )
        )
    response = Response.success(field_types)
    return response


@auto_param()
def load_info(request, project_id, component_id):
    objs = CsvReaderInfo.objects.filter(project_id=project_id, component_id=component_id)
    if len(objs)==0:
        response = Response.fail(ERRORS.COMPONENT_NOT_EXIST, None)
        return response
    response = Response.success(objs[0].magic_name)
    return response


@auto_param
def perview(request, project_id, component_id):
    self_defined_feature = CsvReaderInfo.objects.filter(project_id=project_id, component_id=component_id)
    if len(self_defined_feature)==0:
        return Response.fail(ERRORS.NOT_INITED)
    data_saving_path = mk_working_directory(project_id, component_id, 'data.csv')
    result = list()
    with(open(data_saving_path, 'r', encoding='utf-8')) as f:
        csv_reader = csv.reader(f)
        for row_num, row in enumerate(csv_reader):
            if row_num > 10:
                break
            if len(result) == 0:
                for col in row:
                    result.append(dict(
                        name = col,
                        value = list()
                    ))
            else:
                for column, sample in zip(result, row):
                    column['value'].append(sample)
    return Response.success(result)


def check_target(project_id,input_comp_id,target):
    csv_reader = CsvReaderInfo.objects.filter(project_id=project_id, component_id=input_comp_id)
    if len(csv_reader) == 0:
        return True
    csv_reader = csv_reader[0]
    try:
        assert isinstance(csv_reader, CsvReaderInfo)
        data_saving_path = mk_working_directory(project_id, input_comp_id, csv_reader.file_name)
        csv_reader = pandas.read_csv(data_saving_path, usecols=[target])
        df = pandas.DataFrame(csv_reader)
        detail = dict(df.groupby([target]).size())
        if not set([0, 1]) >= set(list(detail)):
            return True
        return (detail.get(0) < detail.get(1))
    except UnicodeDecodeError as e:
        return True
