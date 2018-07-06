from django.db import models


# class IOFieldType(models.Model):
#     """
#     用于记录数据类型
#     """
#     project_id = models.CharField(max_length=10)
#     component_id = models.CharField(max_length=100)
#     field = models.CharField(max_length=100)
#     field_type = models.CharField(max_length=10)
#     database_type = models.CharField(max_length=50)
#     date_format = models.CharField(max_length=20,null=True)
#     date_size = models.CharField(max_length=20,null=True)
#     ignore = models.BooleanField()
#     selected = models.BooleanField(default=True)


class CompIDGenerator(models.Model):
    """
    用于组件id，生成
    """
    project_id = models.CharField(max_length=10)
    component_id = models.IntegerField()


class CurrentExecution(models.Model):
    """
    记录当前工程正在运行的 Execution，用户在执行该task时，关闭画布，再进入后，可以还原出当前正在执行的任务进度
    """
    project_id = models.CharField(max_length=10)
    current_execution = models.CharField(max_length=20, null=True)

class TaskIDGenerator(models.Model):

    project_id = models.CharField(max_length=10)
    task_id = models.IntegerField()

class TaskRelies(models.Model):

    project_id = models.CharField(max_length=10)
    sc_comp_id = models.CharField(max_length=100)
    tg_comp_id = models.CharField(max_length=100)


class Execution(models.Model):

    task_id = models.CharField(max_length=20)
    project_id = models.CharField(max_length=10)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    status = models.CharField(max_length=20)
    task_count = models.IntegerField()


class Task(models.Model):

    project_id = models.CharField(max_length=10)
    task_id = models.CharField(max_length=20)
    component_id = models.CharField(max_length=100)
    component_type = models.CharField(max_length=20)

    error_code = models.CharField(max_length=30,null=True)
    application_id = models.CharField(max_length=50,null=True)
    tracking_url = models.CharField(max_length=200,null=True)
    detail = models.CharField(max_length=10000, null=True)
    has_log = models.BooleanField(default=False)

    task_status = models.CharField(max_length=20)
    relies = models.IntegerField()
    submit_time = models.DateTimeField(null=True)
    record_time = models.DateTimeField(null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    celery_id = models.CharField(max_length=100,null=True)

# 新增
class FeatureCombine(models.Model):
    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    robotx_spark_id = models.CharField(max_length=100)
    self_defined_feature_id = models.CharField(max_length=100)
    robotx_table_name = models.CharField(max_length=50)


# common
class ModelSyntheticMetrics(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)



class ModelGainLiftSummary(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    group = models.IntegerField()
    cumulative_data_fraction = models.CharField(max_length=100)
    node1lower_threshold = models.CharField(max_length=100)
    node1lift = models.CharField(max_length=100)
    node1cumulative_lift = models.CharField(max_length=100)
    node1response_rate = models.CharField(max_length=100)
    node1cumulative_response_rate = models.CharField(max_length=100)
    node1capture_rate= models.CharField(max_length=100)
    node1cumulative_capture_ratenode1= models.CharField(max_length=100)
    node1gain = models.CharField(max_length=100)
    node1cumulative_gain = models.CharField(max_length=100)


class ModelMaxCriteria(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    metric = models.CharField(max_length=100)
    threshold = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    idx = models.CharField(max_length=100)


class ModelConfusionMatrix(models.Model):
    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    threshold = models.CharField(max_length=100)
    value_type = models.CharField(max_length=100)
    value = models.CharField(max_length=100)


class ModelThresholdsMetric(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    threshold = models.CharField(max_length=100)
    metric = models.CharField(max_length=100)
    value = models.CharField(max_length=100)


class ModelTopnMetricList(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    score_topN = models.CharField(max_length=100)
    tps = models.CharField(max_length=100)
    fps = models.CharField(max_length=100)
    tns = models.CharField(max_length=100)
    fns = models.CharField(max_length=100)
    recall = models.CharField(max_length=100)
    precision = models.CharField(max_length=100)
    accuracy = models.CharField(max_length=100)
    specificity = models.CharField(max_length=100)


class ModelScoreGroupThreshold(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    threshold = models.CharField(max_length=100)
    score_bins = models.CharField(max_length=100)
    tps = models.CharField(max_length=100)
    fps = models.CharField(max_length=100)
    tns = models.CharField(max_length=100)
    fns = models.CharField(max_length=100)
    recall = models.CharField(max_length=100)
    precision = models.CharField(max_length=100)
    accuracy = models.CharField(max_length=100)
    specificity = models.CharField(max_length=100)


# learn

class ModelKFoldsSummary(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    metric = models.CharField(max_length=100)
    value_type = models.CharField(max_length=20)
    value = models.CharField(max_length=100)

class ModelVariableImportance(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    variable = models.CharField(max_length=100)
    relative_importance = models.CharField(max_length=100)
    scaled_importance = models.CharField(max_length=100)
    percentage = models.CharField(max_length=100)

class ModelCoefficient(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    coefficient = models.CharField(max_length=100)
    standardized_coefficient = models.CharField(max_length=100)

class ModelBestParams(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

class ModelSummary(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    layer = models.IntegerField()
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)


class ModelDescription(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    algorithm = models.CharField(max_length=50)
    target = models.CharField(max_length=200)
    tuning_metric = models.CharField(max_length=20, default='AUC')
    n_folds = models.IntegerField(null=True)
    train_percent = models.IntegerField(null=True)
    validation_percent = models.IntegerField(null=True)


# act

class ModelPredictionBIns(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    bin = models.CharField(max_length=100)
    value = models.CharField(max_length=100)


# FeatureCombine
class FeatureCombineRelation(models.Model):

    project_id = models.CharField(max_length=10)
    component_id = models.CharField(max_length=100)
    robotx_field = models.CharField(max_length=100)
    self_defined_field = models.CharField(max_length=100)