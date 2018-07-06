import json

from deepdiff import DeepDiff

import setting
from comm_model.apps import COMPONENTS
from comm_model.components.AtomCommon import extract_component_type

from comm_model.components.AtomLearn import AtomLearn
from comm_model.components.Component import Component
from comm_model.components.FeatureCombine import FeatureCombine
from comm_model.components.RobotX import RobotX
from atom_act.models import AtomAct as AtomActModel
from comm_model.models import ModelPredictionBIns
from comm_model.tasks import atom_act_execute
from common.UTIL import mk_working_directory, to_json
from csv_reader.models import CsvReaderInfo


# class Config_:
#
#     def __init__(self,hive_table, act_data_path, learn_fold_path, act_fold_path):
#         self.hive_table = hive_table
#         self.act_data_path = act_data_path
#         self.act_fold_path = act_fold_path
#         self.learn_fold_path = learn_fold_path

class Config:

    def __init__(self,newdata__filename, reason_code__nvars, ncores,output__dir):

        # newdata.filename 预测数据文件名
        # reason_code.nvars 用于进行reason
        # code分析的变量个数
        # ncores 并行计算所用核数
        # output.dir  输出文件夹名

        self.newdata__filename = newdata__filename
        self.reason_code__nvars = reason_code__nvars
        self.ncores = ncores
        self.output__dir = output__dir



class AtomAct(Component):

    PREDICTION_BIN = "prediction_bins.json"
    PREDICTION_CSV = "prediction.csv"
    COMPONENT_TYPE = COMPONENTS.ATOM_ACT

    TASK_RELY = atom_act_execute
    CONFIG_FILE_NAME = "atom_act.json"

    def __init__(self, project_id, component_id):
        super().__init__(project_id, component_id)
        self.config = None # type: Config

    def __load_from_db__(self):
        project_id = self.project_id
        component_id = self.component_id

        atom_act_model = AtomActModel.objects.filter(project_id=project_id,component_id=component_id)
        if len(atom_act_model) == 0:
            raise Exception("ATOM ACT NOT CONFIGURED")
        atom_act_model = atom_act_model[0]
        assert isinstance(atom_act_model, AtomActModel)

        input_comp_id = atom_act_model.input_comp_id
        atom_learn_id = atom_act_model.atom_learn_id
        reason_code__nvars = atom_act_model.reason_code_nvars
        ncores = atom_act_model.ncores

        # 测试数据路径
        newdata__filename = None
        input_comp_type = extract_component_type(input_comp_id)
        if input_comp_type == COMPONENTS.CSV_READER:
            # hive reader
            csv_header = CsvReaderInfo.objects.filter(project_id=project_id, component_id=input_comp_id)
            if len(csv_header) == 0:
                raise Exception("ATOM LEARN INPUT HIVE READER NOT FOUND")
            csv_header = csv_header[0]
            assert isinstance(csv_header, CsvReaderInfo)
            input_table = csv_header.magic_name
            input_id = csv_header.component_id
            file_name = csv_header.file_name
            # newdata__filename = "%s.%s" %(setting.HIVE_INPUT_DB, input_table)
            newdata__filename = "%s/%s" %(Component.cluster_working_directory(project_id, input_id), file_name)
        elif input_comp_type == COMPONENTS.ROBOTX:
            newdata__filename = RobotX.output_table(project_id, input_comp_id)
        elif input_comp_type == COMPONENTS.FEATURE_COMBINE:
            newdata__filename = FeatureCombine.output_table(project_id, input_comp_id)

        # 模型路径
        learn_fold_path = AtomLearn.learn_fold_path(project_id, atom_learn_id)
        # act输出路径
        output__dir = self.act_fold_path(project_id, component_id)

        self.config = Config(newdata__filename, reason_code__nvars, ncores, output__dir)

    def __eq__(self, other):
        diff = DeepDiff(self.config, other.config)
        return len(diff) == 0

    def prepare(self):
        config_json = to_json(self.config, indent=4)
        config_json = config_json.replace("__",".")
        config_path = AtomAct.get_config_path(self.project_id, self.component_id)
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_json)

    @staticmethod
    def get_config_path(project_id, component_id):
        return mk_working_directory(project_id, component_id, AtomAct.CONFIG_FILE_NAME)

    @staticmethod
    def act_fold_path(project_id, component_id):
        # return setting.WORKING_DIRECTORY + "/%s/%s" %(project_id,component_id)
        return setting.WORKING_DIRECTORY + "/%s" % (project_id)

    @staticmethod
    def act_data_export_path(project_id, component_id):
        return setting.WORKING_DIRECTORY + "/%s/%s/data.csv" % (project_id, component_id)

    @staticmethod
    def get_prediction_bin_local_path(project_id, component_id):
        return mk_working_directory(project_id, component_id, AtomAct.PREDICTION_BIN)

    @staticmethod
    def get_prediction_bin_hdfs_path(project_id, component_id):
        return setting.WORKING_DIRECTORY + "/%s/%s/ACT/%s" % (project_id, component_id,
                                                              AtomAct.PREDICTION_BIN)

    @staticmethod
    def get_prediction_csv_local_path(project_id, component_id):
        return mk_working_directory(project_id, component_id, AtomAct.PREDICTION_CSV)

    @staticmethod
    def get_prediction_csv_hdfs_path(project_id, component_id):
        return setting.WORKING_DIRECTORY + "/%s/%s/ACT/%s" % (project_id, component_id,
                                                              AtomAct.PREDICTION_CSV)
    @staticmethod
    def generate_report(project_id, component_id):
        prediction_bins = AtomAct.get_prediction_bin_local_path(project_id, component_id)
        with open(prediction_bins, "r") as f:
            prediction_bins = json.load(f)['score_bins']

        ModelPredictionBIns.objects.filter(project_id=project_id, component_id=component_id).delete()
        bulk_list = list()
        interval = [i/100.0 for i in range(1, 101)]
        for intv, v in zip(interval,prediction_bins):
            bulk_list.append(
                ModelPredictionBIns(
                    project_id = project_id,
                    component_id = component_id,
                    bin = "%.2f-%.2f" %(intv-0.01, intv),
                    value = v
                )
            )
        ModelPredictionBIns.objects.bulk_create(bulk_list)
