import os
from typing import List

# Create your views here.

# from comm_model.models import CsvReaderInfotype
from comm_model.apps import COMPONENTS
from common import ERRORS
from common.UTIL import auto_param, Response
from csv_reader.apps import FieldType
from csv_reader.models import CsvReaderInfo, CsvReaderInfotype
# from robot_x.apps import StructureClass
from setting import WORKING_DIRECTORY
from .models import Container,Relation

def component_id_validate(id: str, prefix):
    if not id.startswith(prefix):
        return Response.fail(ERRORS.COMPONENT_ID_ERROR,
                             '%s not start with %s' % (id, prefix))

class Join:
    def __init__(self, sc_field, tg_field):
        self.sc_field = sc_field
        self.tg_field = tg_field

@auto_param()
def save_xml(request, project_id, component_id, xml):
    saving_path = os.path.join(WORKING_DIRECTORY, project_id, component_id)
    if not os.path.exists(saving_path) or not os.path.isdir(saving_path):
        os.makedirs(saving_path)
    with open(os.path.join(saving_path, "robot_x.xml"), 'w') as f:
        f.write(xml)
    return Response.success()

@auto_param()
def load_xml(request, project_id, component_id):
    config_path = os.path.join(WORKING_DIRECTORY, project_id, component_id, "robot_x.xml")
    if not os.path.exists(config_path):
        return Response.success('')

    with open(config_path, 'r') as f:
        xml = "".join(f.readlines())
        return Response.success(xml)

@auto_param()
def load_configuration(request, project_id, component_id, inputs: List[str]):
    data_changed = Response.success("changed")

    fields_map = dict()
    containers = Container.objects.filter(project_id=project_id, component_id=component_id)
    if len(containers) == 0:
        return Response.success()

    container = containers[0]
    fields_map[container.container_id] = set(container.key_fields.split(","))
    # 检查 container_id 是否在 inputs 中
    if container.container_id not in inputs:
        containers.delete()
        Relation.objects.filter(project_id=project_id, component_id=component_id).delete()
        return data_changed
    # 检查表名
    container_table_name_check = CsvReaderInfo.objects.filter(project_id=project_id, component_id=container.container_id,
                                                            magic_name=container.table_name)
    if len(container_table_name_check) == 0:
        containers.delete()
        Relation.objects.filter(project_id=project_id, component_id=component_id).delete()
        return data_changed
    # 检查所有关系的source target 是否在 inputs中
    relations = Relation.objects.filter(project_id=project_id, component_id=component_id)
    relation_mess = []
    for relation in relations:
        if relation.source not in inputs:
            relations.delete()
            return data_changed
        relation_table_check = CsvReaderInfo.objects.filter(project_id=project_id, component_id=relation.source,
                                                        magic_name=relation.source_table_name)
        if len(relation_table_check) == 0:
            relations.delete()
            return data_changed
        # 构造在关系中，出现的字段，用于判断，数据是否变更
        sc_field = relation.sc_join.split(",")
        if relation.source in fields_map:
            fields_map[relation.source] |= set(sc_field)
        else:
            fields_map[relation.source] = set(sc_field)
        tg_field = relation.tg_join.split(",")
        if relation.target in fields_map:
            fields_map[relation.target] |= set(tg_field)
        else:
            fields_map[relation.target] = set(tg_field)
        relation_mess.append(dict(
            source=relation.source,
            target=relation.target,
            rel_type=relation.rel_type,
            interval=relation.interval,
            join=[
                {
                    'sc_field': sc,
                    'tg_field': tg
                }
                for sc, tg in zip(sc_field, tg_field)
            ]
        ))
    # 检查container记录的key_fields,relation中的字段 是否在对应表的字段中
    for comp_id, fields in fields_map.items():
        if not field_in_table(fields, project_id, comp_id):
            containers.delete()
            Relation.objects.filter(project_id=project_id, component_id=component_id).delete()
            return data_changed

    container_mess = dict(
        container_id=container.container_id,
        key_fields=container.key_fields.split(",")
    )
    return Response.success(dict(
        container=container_mess,
        relations=relation_mess
    ))


def field_in_table(fields, project_id, component_id):
    table_fields = CsvReaderInfotype.objects.only('field').filter(project_id=project_id, component_id=component_id)
    table_fields_set = set()
    for table_field in table_fields:
        table_fields_set.add(table_field.field)
    return table_fields_set >= fields


@auto_param()
def delete_relation(request, project_id, component_id, source, target):
    Relation.objects.filter(project_id=project_id, component_id=component_id, source=source, target=target).delete()
    return Response.success()


@auto_param()
def save_relation(request, project_id, component_id, source, source_table_name, target, target_table_name,
                  join: List[Join], rel_type, interval = None):

    Relation.objects.filter(project_id=project_id, component_id=component_id, source=source, target=target).delete()
    Relation(project_id=project_id, component_id=component_id, source=source, target=target,
             source_table_name=source_table_name,
             target_table_name=target_table_name,
             sc_join=",".join([v.sc_field for v in join]),
             tg_join=",".join([v.tg_field for v in join]),
             rel_type=rel_type, interval=interval).save()
    return Response.success()


@auto_param()
def save_container(request, project_id, component_id, table_name, container_id, key_fields: List[str]):
    # 检查robotx id是否合法
    check_robotx = component_id_validate(component_id, COMPONENTS.ROBOTX)
    if check_robotx is not None:
        return check_robotx
    # 检查container id 是否合法
    check_container = component_id_validate(component_id, COMPONENTS.CSV_READER)
    if check_robotx is not None:
        return check_container

    Container.objects.filter(project_id=project_id, component_id=component_id).delete()
    Container(project_id=project_id, component_id=component_id, table_name=table_name, container_id=container_id,
              key_fields=",".join(key_fields)).save()
    return Response.success()

container_query_sql_lst = [
    "select a.*",
    "from csv_reader_infotype a",
    "	INNER JOIN container b on a.project_id = b.project_id and a.component_id = b.container_id",
    "where a.project_id = '{project_id}'",
    "	and b.component_id = '{component_id}'"
]
container_query_sql = "\n".join(container_query_sql_lst)

@auto_param()
def container_fields(request, project_id, component_id):
    query_sql = container_query_sql.format(
        project_id = project_id,
        component_id = component_id
    )
    field_types = list(CsvReaderInfotype.objects.raw(query_sql))
    if len(field_types) == 0:
        return Response.success()
    structures = []
    for db_field_type in field_types:
        structure = FieldType(db_field_type.field,
                  db_field_type.selected,
                  db_field_type.field_type,
                  db_field_type.date_format,
                  db_field_type.sample_data)
        structures.append(structure)
    return Response.success(structures)