import copy

from deepdiff import DeepDiff

import setting
from comm_model.apps import COMPONENTS
from comm_model.components.Component import Component
from comm_model.tasks import robotx_execute
from common.UTIL import mk_working_directory, to_json
from csv_reader.models import CsvReaderInfo,CsvReaderInfotype
from robot_x.models import Relation


class CONFIG:
    def __init__(self):
        self.data = dict()
        self.data_describe = dict()
        self.entity_feat = dict()
        self.relation_feat = dict()

    def add_data(self, key, data):
        self.data[key] = data

    def add_numeric(self, table, field):
        if table not in self.data_describe:
            self.data_describe[table] = TableDescribe()
        self.data_describe[table].add_numeric(field)

    def add_factor(self, table, field):
        if table not in self.data_describe:
            self.data_describe[table] = TableDescribe()
        self.data_describe[table].add_factor(field)

    def add_date(self, table, name, date_format):
        if table not in self.data_describe:
            self.data_describe[table] = TableDescribe()
        self.data_describe[table].add_date(name, date_format)

    def add_relation_feat(self, table, target,on):
        table = "_".join([table,"f"])
        if table not in self.relation_feat:
            self.relation_feat[table] = Table(target)
        self.relation_feat[table].add_on(on)


    def add_entity_feat(self,table):
        if table not in self.entity_feat:
            self.entity_feat[table] = Entity(table)

    def add_entity_feat_data(self,table,data):
        if table not in self.entity_feat:
            self.entity_feat[table] = Entity(table)
        self.entity_feat[table].add_process(data)

    def check_entity_feat_data(self,table):
        if table not in self.entity_feat:
            self.entity_feat[table] = Entity(table)
        entry = self.entity_feat[table]
        if len(entry.process) == 0:
            del entry.process


# ==============================table

class Entity:
    def __init__(self, generate_table):
        self.generate_table = "_".join([generate_table,"f"])
        self.process = list()

    def add_process(self,data):
        self.process.append(data)

class Table:

    def __init__(self, target):
        self.target = target
        self.on = list()
        self.method = list()

    def add_on(self,rel):
        self.on.append(rel)

    def add_method(self,method):
        self.method.append(method)

class Detail:

    def __init__(self):
        self.detail = dict()

    def add_data(self, table, hive_table):
        path_data = Path(hive_table)
        self.detail[table] = path_data

class On:
    def __init__(self, a, b):
        self.a = a
        self.b = b


# class Method:
#     def __init__(self, method, interval, numeric):
#         self.method = method
#         self.interval = interval
#         self.numeric = numeric
#         self.summary_method = list()
#
#     def add_summary_method(self, value):
#         self.summary_method.append(value)


class Rel:
    def __init__(self, source, target, type, interval=None):
        self.source = source
        self.target = target
        self.type = type
        # todo 前段modify
        if interval is not None and interval != '':
            self.interval = [int(interval)]
        self.join = list()

    def add_join(self, sc_field, tg_field):
        join = On(sc_field, tg_field)
        self.join.append(join)


class DataDescribe:
    def __init__(self, table):
        self.table = table


class Path:
    def __init__(self, value):
        self.path = value


class TableDescribe:
    def __init__(self):
        self.numeric = set()
        self.date = set()
        self.factor = set()

    def add_numeric(self, name):
        self.numeric.add(name)

    def add_factor(self, name):
        self.factor.add(name)

    def add_date(self, name, date_format):
        date = Date(name, date_format)
        self.date.add(date)

class Method:
    def add_method(self,method):
        self.method = method

    def add_numeric(self,numeric):
        self.numeric = numeric

    def add_field(self,field):
        self.field = field

    def add_interval(self,interval):
        self.interval = interval

    def add_summary_method(self):
        self.summary_method = ['sum', 'avg', 'max', 'min']

    def add_recent_n(self, n):
        self.recent_n = n

class Date:
    FORMATS = dict(
        year="yyyy",
        month="yyyy-MM",
        day="yyyy-MM-dd",
        hour="yyyy-MM-dd hh",
        minute="yyyy-MM-dd hh:mm",
        second="yyyy-MM-dd hh:mm:ss"
    )

    def __init__(self, name, date_format):
        self.name = name
        self.date_format = Date.FORMATS[date_format]


class RobotX(Component):

    COMPONENT_TYPE = COMPONENTS.ROBOTX
    CONFIG_FILE_NAME = "robotx_config.json"
    DATA_FILE_NAME = "data.csv"
    DICT_FILE_NAME = "dict.csv"

    TASK_RELY = robotx_execute
    #
    def __init__(self, project_id, component_id):
        super().__init__(project_id, component_id)
        self.config = CONFIG()

    def __load_from_db__(self):
        self.config.data.update(setting.ROBOT_X_DB_CONFIG)
        # for key in setting.ROBOT_X_DB_CONFIG:
        #     self.config.data[key]=setting.ROBOT_X_DB_CONFIG.get(key)

        relations = Relation.objects.filter(project_id=self.project_id, component_id=self.component_id)
        if len(relations)==0:
            raise Exception("%s %s no relation found" %(self.project_id, self.component_id))

        tables = set()
        source_tables = set()
        for relation in relations:
            assert isinstance(relation, Relation)
            sc_join = relation.sc_join.split(",")
            tg_join = relation.tg_join.split(",")
            joins = zip(sc_join, tg_join)
            tables.add(relation.source)
            tables.add(relation.target)
            source_tables.add(relation.source)

            fields = CsvReaderInfotype.objects.filter(project_id=relation.project_id, component_id=relation.source,
                                                      selected=True)
            field_types = {field.field: field.field_type for field in fields}

            for a, b in joins:
                on = On(a, b)
                self.config.add_relation_feat(relation.source_table_name, relation.target_table_name, on)

            if relation.rel_type == 'FORWARD':
                pass
            elif relation.interval is None or relation.interval == '':
                for method_name in ['sum', 'avg', 'max', 'min']:
                    method = Method()
                    method.add_method(method_name)
                    method.add_field("*")
                    self.config.relation_feat[relation.source_table_name + "_f"].add_method(method)
            else:
                for method_name in ['wma', 'wdiff', 'recent']:
                    method = Method()
                    method.add_method(method_name)
                    method.add_summary_method()
                    method.add_interval(relation.interval)
                    method.add_numeric("*")
                    if method_name == 'recent':
                        method.add_recent_n(1)
                    self.config.relation_feat[relation.source_table_name + "_f"].add_method(method)

            self.config.add_entity_feat(relation.source_table_name)
            # entry
            for field in fields:
                if (field.field in sc_join) or (field.field_type != "factor" ):
                    continue
                process = dict()
                process.update({"type": "oneHot", "oneHot_field": field.field})
                self.config.add_entity_feat_data(relation.source_table_name, process)
            # self.config.check_entity_feat_data(relation.source_table_name)


        input_csv_headers = CsvReaderInfo.objects.filter(project_id=self.project_id, component_id__in=tables)
        if len(input_csv_headers)<len(tables):
            raise Exception("input csvReader table may be deleted")
        csv_reader_id_name_map = dict()
        # data
        detail = Detail()
        for input in input_csv_headers:
            detail.add_data(input.magic_name, self.file_path(input.project_id,input.component_id,input.file_name))
            csv_reader_id_name_map[input.component_id] = input.magic_name
        self.config.add_data("detail",detail.detail)

        # entity_feat
        # relation_feat
        fields = CsvReaderInfotype.objects.filter(project_id=self.project_id, component_id__in=tables, selected=True)
        for field in fields:
            table = csv_reader_id_name_map[field.component_id]
            field_name = field.field
            field_type = field.field_type
            date_format = field.date_format
            if field_type == 'numeric':
                self.config.add_numeric(table, field_name)
            elif field_type == 'factor':
                self.config.add_factor(table, field_name)
            else:
                self.config.add_date(table, field_name, date_format)

    def __eq__(self, other):
        diff = DeepDiff(self.config, other.config)
        return len(diff) == 0

    def prepare(self):
        config_json = to_json(self.config, indent=4)
        config_json = config_json.replace("__",".")
        config_path = mk_working_directory(self.project_id, self.component_id, RobotX.CONFIG_FILE_NAME)
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_json)

    @property
    def get_config_path(self):
        return mk_working_directory(self.project_id, self.component_id, RobotX.CONFIG_FILE_NAME)

    @property
    def output(self):
        output_path = self.output_table(self.project_id, self.component_id)
        output_dict = self.output_dict(self.project_id, self.component_id)
        return output_path, output_dict

    @staticmethod
    def output_table(project_id, component_id):
        return "%s.rbx_%s_%s" %(setting.WORKING_DIRECTORY, project_id, component_id)

    @staticmethod
    def file_path(project_id, component_id,file):
        return "%s/%s/%s/%s" %(setting.WORKING_DIRECTORY, project_id, component_id,file)


    @staticmethod
    def output_dict(project_id, component_id):
        return "%s/%s/%s" %(setting.WORKING_DIRECTORY, project_id, RobotX.COMPONENT_TYPE)
        # return "%s/%s" % (Component.cluster_working_directory(project_id, component_id), RobotX.COMPONENT_TYPE)

    @staticmethod
    def output_data(project_id, component_id):
        return "%s/%s" % (Component.cluster_working_directory(project_id, component_id), RobotX.DATA_FILE_NAME)

