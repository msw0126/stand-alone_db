import setting
import copy

ALGORITHMS = [dict(
    name = algorithm['name'],
    full_name = algorithm['full_name'],
    chinese = algorithm['chinese'],
    description = algorithm['description']
) for algorithm in setting.ALGORITHMS]

ALGORITHM_PARAMS = {
    algorithm['name'] : copy.copy(setting.LEARN_COMMON_PARAMS) + algorithm['params']
    for algorithm in setting.ALGORITHMS
}
