# test_data_filename = "%s/%s" % ("dcgdfhn", "1232434")
# print(test_data_filename )
import copy

import setting

# ALGORITHM_PARAMS = {
#     algorithm: __orderd_dict__(params)
#     for algorithm, params in algorithms.ALGORITHM_PARAMS.items()

ALGORITHM_COMMON_PARAMS = set([param_['name'] for param_ in setting.LEARN_COMMON_PARAMS])

