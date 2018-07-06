import copy
import sys, os, django
sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])))
os.environ["DJANGO_SETTINGS_MODULE"] = "databrain.settings"
django.setup()
from collections import OrderedDict

from csv_reader.models import CsvReaderInfo,CsvReaderInfotype


from comm_model.components.RobotX import RobotX
from comm_model.components import AtomExplore
from atom_explore.views import COMM_PARAMS


from atom_learn import algorithms
from atom_learn.views import __orderd_dict__
from setting import LEARN_COMMON_PARAMS, ALGORITHMS,EXPLORE_COMMON_PARAMS, WORKING_DIRECTORY

# db_save = set(["miss.symbols","quantiles","sample_miss.cutoff","variable_miss.cutoff","variable_zero.cutoff","max.nFactorLevels","discretization","nbins","truncation.cutoff","breaks_zero.cutoff","iv.cutoff","collinearity.cutoff","miss.imputation","unbalanced.cutoff","onehot","normalize","metric","algorithm","hparms","prop.train","ncores","ntree","interaction","shrinkage"])
# print([p["name"]for p in (COMMON_PARAMS) + ALGORITHMS[0]["params"] if p["name"] not in db_save])

# ALGORITHM_PARAMS = {
#     algorithm: __orderd_dict__(params)
#     for algorithm, params in algorithms.ALGORITHM_PARAMS.items()
# }

# print([p["name"]for p in (COMMON_PARAMS) + ALGORITHMS[0]["params"] if p["name"] not in ALGORITHM_PARAMS["gbm"].keys()])

#
# def __orderd_dict__(params):
#     odt = OrderedDict()
#     for param in params:
#         odt[param["name"]] = param
#     return odt

# PARAMS = {
#     algorithm["name"] : algorithm
#     for algorithm in EXPLORE_COMMON_PARAMS
#     }

# ALGORITHM_PARAMS = {
#     algorithm: __orderd_dict__(params)
#     for algorithm, params in {
#         algorithm["name"] : copy.copy(EXPLORE_COMMON_PARAMS)
#         for algorithm in EXPLORE_COMMON_PARAMS
#         }.items()
#     }
# print(ALGORITHM_PARAMS)
# ALGORITHM_COMMON_PARAMS = set([param_["name"] for param_ in ALGORITHM_PARAMS])
# {"lr", "gbm", "lasso", "xgb", "cart", "adaboost", "svm", "rf", "mars", "naivebayes", "auto", "nnet"}
# default_params = ALGORITHM_PARAMS["mars"]
# params = list()
# print(default_params)
# for param in default_params:
#     print(param,"=",default_params[param]["default"])

from common.UTIL import mk_working_directory, to_json
if __name__ == "__main__":
    # robotx = RobotX(27, "RobotX4")
    # robotx.__load_from_db__()
    # config_json = to_json(robotx.config, indent=4)
    # config_json = config_json.replace("__", ".")
    # print(config_json)

    # process = set()
    # process.update({"ghjk":"fghjk"})
    # process.update({"type": "oneHot","oneHot_field":"sub_action_type"})
    # process.update({"type": "oneHot","1oneHot_field":"sub_action_type"})
    # process.update({"type": "oneHot","oneHot_field":"sub_action_type"})
    # process.update({"type": "oneHot","oneHot_field":"sub_action_type"})
    # process.update({"type": "oneHot","oneHot_field":"sub_action_type"})
    # print(process)
    # if "xgb" in ["xgb", "svm", "naivebayes", "lasso", "auto", "nnet", "rf", "svm", "auto"]:
    #     print("ok")
    # a="sretgd"
    # b="11111112"
    # print("%s%s" %(a,b))
    fields = CsvReaderInfotype.objects.filter(project_id="27", component_id="CsvReader0",selected=True)

    print({field.field:field.field_type for field in fields})
