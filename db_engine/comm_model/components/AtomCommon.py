import re
from comm_model.models \
    import \
    ModelSyntheticMetrics, \
    ModelGainLiftSummary,  \
    ModelMaxCriteria,  \
    ModelConfusionMatrix,  \
    ModelThresholdsMetric, \
    ModelTopnMetricList,  \
    ModelScoreGroupThreshold,\
    TaskIDGenerator,\
    CompIDGenerator

from common import ERRORS
# PARAMETER_MISSING_ERROR, GET_DENIED_FOR_THIS_METHOD, NOT_LOGIN, PY4J_CONNECTION_ERROR

param_transform_dict = dict(
    boolean = lambda x,d: x=='true' if 'stand_for' not in d else d['stand_for'][0 if x=='true' else 1],
    bool = lambda x,d: x=='true' if 'stand_for' not in d else d['stand_for'][0 if x=='true' else 1],
    int = lambda x,d:int(x),
    double = lambda x,d:float(x),
    string = lambda x,d:x,
    float = lambda x,d:float(x),
    enum = lambda x,d:str(x),
    list = lambda x,d:list(x)
)


class ParamCheckingError(object):
    def __init__(self, name, error):
        self.name = name
        self.error = error


# 组件公共方法

def extract_component_type(component_id):
    """
    提取组件类型
    :param component_id:
    :return:
    """
    return re.sub('\d+', '', component_id)



def param_transform(description, value_str):
    p_type = description['type']
    p_multiple = description['multiple']
    values = value_str.split(",") if p_multiple else [value_str]
    if value_str !="" and value_str != None and value_str !="None":
        trans_method = param_transform_dict[p_type]
        values = [trans_method(value, description) for value in values]
        return values if p_multiple else values[0]
    else:
        values = None



def report_for_synthetical_metric(model_metrics, project_id, component_id):
    bulk_insert = list()
    synthetical_metric = model_metrics['synthetical_metric_dict']
    for n_, v_ in synthetical_metric.items():
        if n_ in ['AUC', 'Gini', 'r2', 'RMSE', 'logloss', 'MSE', 'AIC']:
            bulk_insert.append(
                ModelSyntheticMetrics(
                    project_id=project_id,
                    component_id=component_id,
                    name=n_,
                    value=str(v_)
                )
            )
    ModelSyntheticMetrics.objects.bulk_create(bulk_insert)


def param_checking(name, value, param_limit):
    if not isinstance(value, str):
        return None
    value = value.strip()
    # if value == "":
    #     return ParamCheckingError(name, ERRORS.EMPTY_PARAM)
    multiple = param_limit["multiple"]
    type_ = param_limit["type"]
    if not multiple:
        if type_ == "int":
            try:
                if value == "":
                    pass
                else:
                    int(value)
            except Exception:
                return ParamCheckingError(name, ERRORS.VALUE_ERROR_PARAM)
        elif type_ == "double" or type_ == "float":
            try:
                float(value)
            except Exception:
                return ParamCheckingError(name, ERRORS.VALUE_ERROR_PARAM)
        elif type_ == "boolean":
            if value not in ["true","false"]:
                return ParamCheckingError(name, ERRORS.VALUE_ERROR_PARAM)
    else:
        values = value.split(",")
        for value in values:
            if type_ == "int":
                try:
                    if value == "":
                        pass
                    else:
                        int(value)
                except Exception:
                    return ParamCheckingError(name, ERRORS.VALUE_ERROR_PARAM)
            elif type_ == "double" or type_ == "float":
                try:
                    float(value)
                except Exception:
                    return ParamCheckingError(name, ERRORS.VALUE_ERROR_PARAM)

# 新增
def get_task_id(project_id):
    query_result = TaskIDGenerator.objects.filter(project_id=project_id)
    if len(query_result) == 0:
        # 没有，task_id返回0，并保存记录到数据库
        TaskIDGenerator(project_id=project_id, task_id=1).save()
        return "%s_%d" % (project_id, 0)
    else:
        # 有，task_id + 0 到 task_id + n -1，返回，并更新数据库
        task_id_generator = query_result[0]
        task_id = task_id_generator.task_id
        task_id_generator.task_id = task_id_generator.task_id + 1
        task_id_generator.save()
        return "%s_%d" % (project_id, task_id)


def execute_components(need_execute, project_id):
    if len(need_execute) == 0:
        # 没有需要执行的组件
        return None
    # get task_id
    task_id = get_task_id(project_id)
    # 之前任务删除，之前依赖删除
    TaskRelies.objects.filter(project_id=project_id).delete()
    for point in need_execute.values():
        relies = 0
        for rely_point in point.relies_bak:
            if rely_point.id in need_execute:
                relies += 1
        executor_class = eval(point.type)
        forwards = None if len(point.forwards) == 0 else [p.id for p in point.forwards]
        executor = executor_class(project_id, point.id)
        assert isinstance(executor, Component)
        # 记录数据库
        executor.record(task_id, relies, forwards)
    Execution(project_id=project_id, task_id=task_id, start_time=datetime.datetime.now(),
              status=ExecutionStatus.RUNNING, task_count=len(need_execute)).save()
    CurrentExecution.objects.update_or_create(project_id=project_id, defaults=dict(
        current_execution=task_id
    ))
    return task_id


def report_for_gains_lift(model_metrics, project_id, component_id):
    bulk_insert = list()
    gains_lift_lst = model_metrics['gains_lift_lst']
    for v_ in gains_lift_lst[1:]:
        bulk_insert.append(
            ModelGainLiftSummary(
                project_id=project_id,
                component_id=component_id,
                group=v_[1],
                cumulative_data_fraction=str(v_[2]),
                node1lower_threshold=str(v_[3]),
                node1lift=str(v_[4]),
                node1cumulative_lift=str(v_[5]),
                node1response_rate=str(v_[6]),
                node1cumulative_response_rate=str(v_[7]),
                node1capture_rate=str(v_[8]),
                node1cumulative_capture_ratenode1=str(v_[9]),
                node1gain=str(v_[10]),
                node1cumulative_gain=str(v_[11])
            )
        )
    ModelGainLiftSummary.objects.bulk_create(bulk_insert)


def report_for_max_criteria(model_metrics, project_id, component_id):
    bulk_insert = list()
    max_criteria_metric_lst = model_metrics['max_criteria_metric_lst']
    for v_ in max_criteria_metric_lst[1:]:
        bulk_insert.append(
            ModelMaxCriteria(
                project_id=project_id,
                component_id=component_id,
                metric=str(v_[0]),
                threshold=str(v_[1]),
                value=str(v_[2]),
                idx=str(v_[3])
            )
        )
    ModelMaxCriteria.objects.bulk_create(bulk_insert)


def report_for_confusion_matrix(model_metrics, project_id, component_id):
    # c_matrix_lst
    bulk_insert = list()
    c_matrix_lst = model_metrics['c_matrix_lst']
    for v_ in c_matrix_lst:
        threshold = int(v_['threshold'] * 100) / 100.0
        value = v_['value']
        head = value[0][1:]
        for vv_ in value[1:]:
            vtype = vv_[0]
            for param_v, hd in zip(vv_[1:], head):
                bulk_insert.append(
                    ModelConfusionMatrix(
                        project_id=project_id,
                        component_id=component_id,
                        threshold=str(threshold),
                        value_type="%s-%s" % (hd, vtype),
                        value=str(param_v)
                    )
                )
    ModelConfusionMatrix.objects.bulk_create(bulk_insert)


def report_for_threshold_metric(model_metrics, project_id, component_id):
    # thresholds_scores_df_s_lst
    bulk_insert = list()
    thresholds_scores = model_metrics['thresholds_scores_df_s_lst']
    head = thresholds_scores[0]

    threshold_idx = [idx for idx,k in enumerate(head) if k=='threshold'][0]

    for v_ in thresholds_scores[1:]:
        threshold = v_[threshold_idx]
        for param_v, param_n in zip(v_, head):
            if param_n == 'threshold':
                continue
            bulk_insert.append(
                ModelThresholdsMetric(
                    project_id=project_id,
                    component_id=component_id,
                    threshold=str(threshold),
                    metric=param_n,
                    value=str(param_v)
                )
            )
    ModelThresholdsMetric.objects.bulk_create(bulk_insert)


def report_for_topN_metric_List(model_metrics, project_id, component_id):
    bulk_insert = list()
    topn_metrics_10_lst = model_metrics['topn_metrics_10_lst']
    for topn_metrics_i in topn_metrics_10_lst[1:]:
        bulk_insert.append(
            ModelTopnMetricList(
                project_id=project_id,
                component_id=component_id,
                score_topN=topn_metrics_i[0],
                tps=topn_metrics_i[1],
                fps=topn_metrics_i[2],
                tns=topn_metrics_i[3],
                fns=topn_metrics_i[4],
                recall=topn_metrics_i[5],
                precision=topn_metrics_i[6],
                accuracy=topn_metrics_i[7],
                specificity=topn_metrics_i[8]
            )
        )
    ModelTopnMetricList.objects.bulk_create(bulk_insert)


def report_for_score_group_threshold(model_metrics, project_id, component_id):
    bulk_insert = list()
    score_group_threshold_10_dict = model_metrics['score_group_threshold_10_dict']
    score_group_threshold_10_dict = sorted(score_group_threshold_10_dict, key=lambda x: float(x['threshold']))
    for v_ in score_group_threshold_10_dict:
        threshold = int(float(v_['threshold']) * 100) / 100.0
        value = v_['value']
        for group_v in value[1:]:
            bulk_insert.append(
                ModelScoreGroupThreshold(
                    project_id=project_id,
                    component_id=component_id,
                    threshold=str(threshold),
                    score_bins=str(group_v[0]),
                    tps=str(group_v[1]),
                    fps=str(group_v[2]),
                    tns=str(group_v[3]),
                    fns=str(group_v[4]),
                    recall=str(group_v[5]),
                    precision=str(group_v[6]),
                    accuracy=str(group_v[7]),
                    specificity=str(group_v[8])
                )
            )
    ModelScoreGroupThreshold.objects.bulk_create(bulk_insert)