import json

from deepdiff import DeepDiff

import setting
from atom_explore.views import COMM_PARAMS
from atom_learn.models import AtomLearn as AtomLearnModel
from atom_learn.models import AtomLearnParam
from atom_learn.views import ALGORITHM_PARAMS
from comm_model.apps import COMPONENTS
from comm_model.components.AtomCommon import report_for_synthetical_metric, report_for_gains_lift, \
    report_for_max_criteria, report_for_confusion_matrix, report_for_threshold_metric, report_for_score_group_threshold, \
    report_for_topN_metric_List, param_transform, extract_component_type
from comm_model.components.AtomExplore import AtomExplore
from comm_model.components.Component import Component
from comm_model.components.FeatureCombine import FeatureCombine
from comm_model.components.RobotX import RobotX
from comm_model.models import \
    ModelDescription, \
    ModelSummary, \
    ModelBestParams, \
    ModelCoefficient, \
    ModelVariableImportance, \
    ModelSyntheticMetrics, \
    ModelKFoldsSummary, \
    ModelMaxCriteria, \
    ModelGainLiftSummary, \
    ModelConfusionMatrix, \
    ModelThresholdsMetric, ModelTopnMetricList, ModelScoreGroupThreshold
from comm_model.tasks import atom_learn_execute
from common.UTIL import mk_working_directory, to_json
from csv_reader.models import CsvReaderInfo,CsvReaderInfotype
from setting import LEARN_COMMON_PARAMS


ALGORITHM_COMMON_PARAMS = set([param_['name'] for param_ in LEARN_COMMON_PARAMS])


class Config:

    def __init__(self,
                 # data__filename, dictionary__filename, id__varname, target__varname,
                 output__dir, algorithm):
        # self.data__filename = data__filename
        # self.dictionary__filename = dictionary__filename
        # self.id__varname = id__varname
        # self.target__varname = target__varname
        self.output__dir = output__dir
        self.algorithm = algorithm
        self.hparms = dict()

    def add_common_param(self, param, value):
        self.__setattr__(param, value)

    def add_hparms(self, param, value):
        self.hparms[param] = value


class AtomLearn(Component):

    COMPONENT_TYPE = COMPONENTS.ATOM_LEARN

    TASK_RELY = atom_learn_execute
    CONFIG_FILE_NAME = "atom_learn.json"
    MODEL_PROPERTIES = "model_properties.json"
    MODEL_METRICS = "model_metrics.json"

    def __init__(self, project_id, component_id):
        super().__init__(project_id, component_id)
        self.config = None # type: Config

    def __load_from_db__(self):
        project_id = self.project_id
        component_id = self.component_id

        atom_learn_model = AtomLearnModel.objects.filter(project_id=project_id,component_id=component_id)
        if len(atom_learn_model) == 0:
            raise Exception("ATOM LEARN NOT CONFIGURED")
        atom_learn_model = atom_learn_model[0]
        assert isinstance(atom_learn_model, AtomLearnModel)

        input_comp_id = atom_learn_model.input_comp_id
        algorithm = atom_learn_model.algorithm

        output__dir = None
        # learn输出路径
        input_comp_type = extract_component_type(input_comp_id)
        if input_comp_type == COMPONENTS.ATOM_EXPLORE:
            output__dir = AtomExplore.explore_fold_path(project_id, component_id)
        else:
            raise Exception("AtomLearn 依赖组件出错" )
        self.config = Config(output__dir, algorithm)
        # data__filename, dictionary__filename, id__varname, target__varname, output__dir ,algorithm

        if algorithm not in ALGORITHM_PARAMS:
            raise Exception("ALGORITHM %s NOT SUPPORTED" %algorithm)

        algorithm_params = ALGORITHM_PARAMS[algorithm]
        atom_learn_param = AtomLearnParam.objects.filter(project_id=project_id,component_id=component_id)
        if len(atom_learn_param)>0:
            if len(algorithm_params)!=len(atom_learn_param):
                raise Exception("ALGORITHM %s LUCK OF PARAMETER" %algorithm)
            for param in atom_learn_param:
                assert isinstance(param, AtomLearnParam)
                param_name = param.param_name
                param_value = param.param_value
                # 转换为真实参数
                param_description = algorithm_params[param_name]
                true_value = param_transform(param_description, param_value)
                if param_name in ALGORITHM_COMMON_PARAMS:
                    # 通用参数
                    self.config.add_common_param(param_name, true_value)
                else:
                    self.config.add_hparms(param_name, true_value)
        if len(self.config.hparms) == 0:
            self.config.hparms = None


    def __eq__(self, other):
        diff = DeepDiff(self.config, other.config)
        return len(diff) == 0

    def prepare(self):
        config_json = to_json(self.config, indent=4)
        config_json = config_json.replace("__",".")
        config_path = AtomLearn.get_config_path(self.project_id, self.component_id)
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_json)

    @staticmethod
    def get_config_path(project_id, component_id):
        return mk_working_directory(project_id, component_id, AtomLearn.CONFIG_FILE_NAME)

    @staticmethod
    def learn_fold_path(project_id, component_id):
        return setting.WORKING_DIRECTORY + "/%s" % (project_id)


    @staticmethod
    def train_data_path(project_id, component_id):
        return setting.WORKING_DIRECTORY + "/%s/%s/data.csv" % (project_id, component_id)

    @staticmethod
    def get_model_properties_local_path(project_id, component_id):
        return mk_working_directory(project_id, component_id, AtomLearn.MODEL_PROPERTIES)

    # @staticmethod
    # def get_model_properties_hdfs_path(project_id, component_id):
    #     return setting.WORKING_DIRECTORY + "/%s/%s/LEARN/%s" % (project_id, component_id,
    #                                                             AtomLearn.MODEL_PROPERTIES)

    @staticmethod
    def get_model_metrics_local_path(project_id, component_id):
        return mk_working_directory(project_id, component_id, AtomLearn.MODEL_METRICS)


    def check_config(self, last_component_ids):
        self.__load_from_db__()
        if (self.config.algorithm in ["naivebayes", "lr"]) and (self.config.hparms != None):
            raise Exception("选择的算法%s不支持高级参数配置"%self.config.algorithm )
        if ( self.config.algorithm in ["xgb", "svm", "naivebayes", "lasso", "auto", "nnet", "rf", "svm", "auto"]):
            for last_component_id in last_component_ids:
                # path = AtomExplore.get_config_path(self.project_id, last_component_id)
                path = setting.WORKING_DIRECTORY + "/%s/%s/%s" % (self.project_id, last_component_id,AtomExplore.CONFIG_FILE_NAME)
                load_dict = None
                with open(path,'r') as load_f:
                    load_dict = json.load(load_f)
                if (self.config.algorithm in ['nnet'] and load_dict["normalize"] != True):
                    raise Exception("%s的配置参数[%s(%s=%s)]不支持%s算法" %( last_component_id,COMM_PARAMS["normalize"]["chinese"],"normalize",load_dict["normalize"],self.config.algorithm))
                if(self.config.algorithm in ['rf', 'svm', 'auto'] and load_dict["miss.imputation"] != True):
                    raise Exception("%s的配置参数[%s(%s=%s)]不支持%s算法" %( last_component_id,COMM_PARAMS["miss.imputation"]["chinese"],"miss.imputation",load_dict["miss.imputation"],self.config.algorithm))
                if(self.config.algorithm in ['xgb', 'svm', 'naivebayes', 'lasso', 'auto'] and load_dict["onehot"] != True) :
                    raise Exception("%s的配置参数[%s(%s=%s)]不支持%s算法" %( last_component_id,COMM_PARAMS["onehot"]["chinese"],"onehot",load_dict["onehot"],self.config.algorithm))
