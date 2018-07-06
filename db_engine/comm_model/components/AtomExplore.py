import copy
from collections import OrderedDict

from deepdiff import DeepDiff

import setting
from atom_explore.views import COMM_PARAMS
from atom_learn import algorithms
from comm_model.apps import COMPONENTS
from comm_model.components.AtomCommon import param_transform, extract_component_type
from comm_model.components.Component import Component
from comm_model.components.RobotX import RobotX
from comm_model.tasks import atom_explore_execute
from atom_explore.models import AtomExplore as AtomExploreModel, AtomExploreParam
from common.UTIL import mk_working_directory, to_json
from csv_reader.models import CsvReaderInfo,CsvReaderInfotype
from robot_x.models import Relation,Container

ALGORITHM_COMMON_PARAMS = [p['name']for p in setting.EXPLORE_COMMON_PARAMS]

class Config:

    def __init__(self,data__filename, dictionary__filename, id__varname, target__varname,output__dir):
        self.data__filename = data__filename
        self.dictionary__filename = dictionary__filename
        self.id__varname = id__varname
        self.target__varname = target__varname
        self.output__dir = output__dir

    def add_common_param(self, param, value):
        self.__setattr__(param, value)


class AtomExplore(Component):
    COMPONENT_TYPE = COMPONENTS.ATOM_EXPLORE
    # 执行任务方法入口
    TASK_RELY = atom_explore_execute
    # 生成配置文件
    CONFIG_FILE_NAME = "atom_explore.json"
    # 输出文件名
    EXPLORE_DICT_FILE = "dict.csv"
    # MODEL_PROPERTIES = "model_properties.json"
    # MODEL_METRICS = "model_metrics.json"

    def __init__(self, project_id, component_id):
        super().__init__(project_id, component_id)
        self.config = None  # type: Config

    def __load_from_db__(self):
        project_id = self.project_id
        component_id = self.component_id

        atom_explore_model = AtomExploreModel.objects.filter(project_id=project_id, component_id=component_id)
        if len(atom_explore_model) == 0:
            raise Exception("ATOM EXPLORE NOT CONFIGURED")
        atom_explore_model = atom_explore_model[0]
        assert isinstance(atom_explore_model, AtomExploreModel)

        input_comp_id = atom_explore_model.input_comp_id
        feature_id = atom_explore_model.feature_id
        feature_target = atom_explore_model.feature_target

        # data.filename 数据文件名
        data__filename = None
        # dictionary.filename 字典文件名
        dictionary__filename = None
        # 训练数据路径
        input_comp_type = extract_component_type(input_comp_id)
        if input_comp_type == COMPONENTS.CSV_READER:
            # csv_reader
            csv_reader = CsvReaderInfo.objects.filter(project_id=project_id, component_id=input_comp_id)
            if len(csv_reader) == 0:
                raise Exception("ATOM EXPLORE INPUT CSVREADER NOT FOUND")
            csv_reader = csv_reader[0]
            assert isinstance(csv_reader, CsvReaderInfo)
            input_file = csv_reader.file_name
            data__filename = "%s/%s" % (mk_working_directory(project_id, input_comp_id), input_file)
            # 生成数据字典
            io_field_types = CsvReaderInfotype.objects.filter(project_id=project_id, component_id=input_comp_id,
                                                              selected=True)
            with open(AtomExplore.csv_reader_dict_path(project_id, component_id), 'w', encoding='utf-8') as f:
                lines = list()
                lines.append("variable,type\n")
                for io_f_type_ in io_field_types:
                    assert isinstance(io_f_type_, CsvReaderInfotype)
                    if io_f_type_.field_type not in ["factor","numeric"]:
                        continue
                    lines.append('"%s",%s\n' % (io_f_type_.field, io_f_type_.field_type))
                f.writelines(lines)
            dictionary__filename = AtomExplore.csv_reader_dict_path(project_id, component_id)
        elif input_comp_type == COMPONENTS.ROBOTX:
            # robotx
            # relations = Relation.objects.filter(project_id=project_id,component_id=input_comp_type)
            containers = Container.objects.filter(project_id=project_id,component_id=input_comp_id)
            # if len(relations)==0:
            #     raise Exception("ATOM EXPLORE INPUT ROBOTX-RELATION NOT FOUND")
            if len(containers)==0:
                raise Exception("ATOM EXPLORE INPUT ROBOTX-CONTAINER NOT FOUND")
            # relation = relations[0]
            container = containers[0]
            csvReaders = CsvReaderInfo.objects.filter(project_id=project_id, component_id=container.container_id)
            # csvReader1 = CsvReaderInfo.objects.filter(project_id=project_id, component_id=relation.target)
            if len(csvReaders) == 0:
                raise Exception("ATOM EXPLORE INPUT ROBOTX-CSVREADER NOT FOUND")
            dictionary__filename = RobotX.output_dict(project_id,input_comp_type)
            data__filename = "%s/%s" % (Component.cluster_working_directory(project_id, csvReaders[0].component_id), csvReaders[0].file_name)
        # explore输出路径
        output__dir = self.explore_fold_path(project_id, component_id)
        self.config = Config(data__filename, dictionary__filename, feature_id, feature_target, output__dir)
        # data__filename, dictionary__filename, id__varname, target__varname, output__dir

        algorithm_params = setting.EXPLORE_COMMON_PARAMS
        atom_explore_param = AtomExploreParam.objects.filter(project_id=project_id, component_id=component_id)
        if len(algorithm_params) != len(atom_explore_param):
            raise Exception("ALGORITHM %s LUCK OF PARAMETER" % str(ALGORITHM_COMMON_PARAMS))
        for param in atom_explore_param:
            assert isinstance(param, AtomExploreParam)
            param_name = param.param_name
            param_value = param.param_value
            # 转换为真实参数
            param_description = COMM_PARAMS[param_name]
            true_value = param_transform(param_description, param_value)
            if param_name in ALGORITHM_COMMON_PARAMS:
                # 通用参数
                self.config.add_common_param(param_name, true_value)

    def __eq__(self, other):
        diff = DeepDiff(self.config, other.config)
        return len(diff) == 0

    def prepare(self):
        config_json = to_json(self.config, indent=4)
        config_json = config_json.replace("__", ".")
        config_path = AtomExplore.get_config_path(self.project_id, self.component_id)
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_json)

    @staticmethod
    def get_config_path(project_id, component_id):
        return mk_working_directory(project_id, component_id, AtomExplore.CONFIG_FILE_NAME)

    @staticmethod
    def get_data_dir_path(project_id, component_id,file_name):
        return mk_working_directory(project_id, component_id, file_name)

    @staticmethod
    def explore_fold_path(project_id, component_id):
        # return setting.WORKING_DIRECTORY + "/%s/%s" % (project_id,component_id)
        return setting.WORKING_DIRECTORY + "/%s" % (project_id)

    @staticmethod
    def csv_reader_dict_path(project_id, component_id):
        return mk_working_directory(project_id, component_id, AtomExplore.EXPLORE_DICT_FILE)

    @staticmethod
    def train_data_path(project_id, component_id):
        return setting.WORKING_DIRECTORY + "/%s/%s/data.csv" % (project_id, component_id)


