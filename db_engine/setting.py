# 数据库配置
import os

# ===新增====
HIVE_OUTPUT_DB= "default"
HIVE_INPUT_DB = "default"
# ===========

# mysql数据库配置
DB_DATABRAIN = 'django.db.backends.mysql'
DB_NAME = 'engine'
DB_USER = 'root'
DB_PASSWORD = 'taoshu12345'
DB_HOST = 'localhost'
DB_PORT = '3306'

# robot_x postgreSQL数据库配置
ROBOT_X_DB_CONFIG = {"user_name":"postgres","password":"taoshu12345"}

# 文件上传的参数
WORKING_DIRECTORY="/home/taoshu/static/WORKING_DIRECTORY"
DEVELOP_MODE=""
DEVELOP_ACCOUNT=""
DEVELOP_PASSWD=""

# 执行文件配置
COMPONENT_DIR = "/home/taoshu/static/COMPONENT_DIR/Atom7.2"
ATOM_PATH = os.path.join(COMPONENT_DIR, "Atom")
ROBOTX_PATH = os.path.join(COMPONENT_DIR,"robotx", "robotx")
FEATURE_COMBINE_PATH = os.path.join(COMPONENT_DIR, "FeatureCombine")
# 日志文件
LICATION_URL = "/home/taoshu/static/logs/db_engine"
# LICATION_URL = "http://localhost:15672/apps"
APPLICATION_URL = LICATION_URL + "/{app_id}"
APPLICATION_ATTEMPT_URL = APPLICATION_URL + "/log"
JOB_SERVER_LOG_URL = APPLICATION_ATTEMPT_URL + "/{node}/{container}/{container}/{user}"
APPLICATION_KILL_URL = APPLICATION_URL + "/state"
LOG_QUERY_PERIOD = 10

# celery配置
import djcelery
djcelery.setup_loader()
BROKER_URL = 'amqp://guest:guest@localhost:5672/'
CELERY_RESULT_BACKEND = 'amqp://guest@localhost:5672/'

##atom组件算法的静态值
DEFAULT_ALGORITHM = "gbm"
ALGORITHMS = [
    # dict(name="GBDT",full_name="GBDT",chinese="",description="",params=[dict(name="ntrees",chinese="ntrees",description="树个数",multiple=True,default="3000",type = "int",check = dict(min = 10,max = 5000,max_num = 1)),dict(name="interaction",chinese="interaction",description="interaction",multiple=True,default="1,5,10,15,20",type="int",check=dict(min=1,max=100,max_num = 5)),dict(name="shrinkage",chinese="shrinkage",multiple=True,description="shrinkage",default="0.001,0.005,0.01",type="double",check=dict(min=0,max=1.0,max_num = 3)),dict(name="n_minobsinnode",chinese="n_minobsinnode",multiple=True,description="n_minobsinnode",default="5",type="int",check=dict(min=1,max=10,max_num = 1))]),dict(name="Random Forest",full_name="Random Forest",chinese="",description="",params=[dict(name="ntrees",chinese="ntrees",description="树个数",multiple=True,default="100,200,300,500,800,1000",type="int",check=dict(min=100,max=1000,max_num=6)),dict(name="mtry",chinese="mtry",description="mtry",multiple=True,default="5,10,15",type="int",check=dict(min=1,max=100,max_num=3)),dict(name="nodesize",chinese="nodesize",description="nodesize",multiple=True,default="1,2,5,10",type="double",check=dict(min=0,max=100,max_num=4))]),dict(name="CART",full_name="CART",chinese="",description="",params=[dict(name="minsplit",chinese="minsplit",description="minsplit",multiple=True,default="1,2,5,10",type="int",check=dict(min=1,max=10,max_num=5)),dict(name="cp",chinese="cp",description="cp",multiple=True,default="0.001,0.005,0.01",type="float",check=dict(min=0.00,max=1,max_num = 3))]),dict(name="Xgboost",full_name="Xgboost",chinese="",description="",params=[dict(name="eta",chinese="eta",multiple=True,description="eta",default="0.01,0.05,0.1",type="float",check=dict(min=0.00,max=1,max_num=5)),dict(name="nrounds",chinese="nrounds",multiple=True,description="nrounds",default="10000",type="int",check=dict(min=0,max=1e-5,max_num = 1)),dict(name="early_stopping_rounds",chinese="early_stopping_rounds",multiple=True,description="early_stopping_rounds",default="100",type="int",check=dict(min=0,max=1e-5,max_num=2)),dict(name="subsample",chinese="subsample",multiple=True,description="subsample",default="1",type="int",check=dict(min=0,max=1e-5,max_num = 2,decimal = 6)),dict(name="colsample_bytree",chinese="colsample_bytree",multiple=True,description="colsample_bytree",default="0.8,1",type="double",check=dict(min=0,max=1,max_num = 2,decimal = 2)),dict(name="max_depth",chinese="max_depth",multiple=True,description="max_depth",default="6",type="int",check=dict(min=0,max=1e+5,max_num = 1)),dict(name="min_child_weight",chinese="min_child_weight",multiple=True,description="min_child_weight",default="1",type="int",check=dict(min=1e-5,max=1e+5,max_num = 1,decimal = 6)),dict(name="gamma",chinese="gamma",multiple=True,description="gamma",default="0,0.1",type="double",check=dict(min=0,max=1e-5,max_num = 1,decimal = 6)),dict(name="lambda",chinese="lambda",multiple=True,description="lambda",default="0.01,0.1,1",type="double",check=dict(min=0,max=1e-5,max_num = 3,decimal = 6)),dict(name="alpha",chinese="alpha",multiple=True,description="alpha",default="0,0.1,0.5,1",type="double",check=dict(min=0,max=1e-5,max_num = 4,decimal = 6))]),dict(name="SVM",full_name="SVM",chinese="",description="",params=[dict(name="C",chinese="C",multiple=True,description="C",default="0.001,0.01,1,10,100,1000",type="int",check=dict(min=0,max=1e+5,max_num=6,decimal = 6)),dict(name="gamma",chinese="gamma",multiple=True,description="gamma",default="0.001,0.01,0.1,1",type="double",check=dict(min=0,max=1,max_num = 4,decimal = 6))]),dict(name="Naive Bayes",full_name="Naive Bayes",chinese="",description="",params=[]),dict(name="Logistic Regression",full_name="Logistic Regression",chinese="",description="",params=[]),dict(name="LASSO",full_name="LASSO",chinese="",description="",params=[dict(name="lambda",chinese="lambda",multiple=True,description="lambda",default="0.5,1",type="double",check=dict(min=0,max=1,max_num = 2,decimal = 6)),dict(name="alpha",chinese="alpha",multiple=True,description="alpha",default="0.001,0.01,0.1",type="double",check=dict(min=0,max=1,max_num = 3,decimal = 6))]),dict(name="Neural Network",full_name="Neural Network",chinese="",description="",params=[]),dict(name="AdaBoost",full_name="AdaBoost",chinese="",description="",params=[dict(name="minsplit",chinese="minsplit",multiple=True,description="minsplit",default="5,10,20",type="int",check=dict(min=0,max=None,max_num=3)),dict(name="cp",chinese="cp",multiple=True,description="cp",default="0.001,0.005,0.01",type="double",check=dict(min=0,max=1e-2,max_num=3)),dict(name="iter",chinese="iter",multiple=True,description="iter",default="30,50,70",type="int",check=dict(min=0,max=1e+2,max_num=3))]),dict(name="Stacking",full_name="Stacking",chinese="",description="",params=[])
# Learn
    dict(name="gbm",full_name="gbm",chinese="gbm",description="gbm",params=[
    dict(name="ntree", chinese="树的棵数", multiple=True, default=3000, type="int", check=dict(min=10, max=10000, max_num=5),description="树的棵数" ),
    dict(name="interaction", chinese="特征交叉最大深度",description="特征交叉最大深度", multiple=True, default="1,5,10,15,20", type="int", check=dict(min=1, max=100, max_num=5,),),
    dict(name="shrinkage", chinese="学习步长", description="学习步长", multiple=True, default="0.001,0.005,0.01", type="float", check=dict(min=0, max=1, max_num=5, ), ),
    dict(name="n.minobsinnode", chinese="叶节点最少保留样本数", multiple=True, default=5, type="int", check=dict(min=1, max=100, max_num=5, ), )]),
    dict(name="rf",full_name="rf",chinese="rf",description="rf",params=[
    dict(name="ntree", chinese="数的棵数", description="数的棵数", multiple=True, default="50,100,200,300,400,500,1000", type="int", check=dict(min=10, max=10000, max_num=10), ),
    dict(name="nodesize", chinese="样本数",description="叶节点最少保留样本数", multiple=True, default=5, type="int", check=dict(min=1, max=100, max_num=5), ),]),
    dict(name="xgb",full_name="xgb",chinese="xgb",description="xgb",params=[
    dict(name="eta", chinese="学习步长", description="学习步长", multiple=True, default="0.001,0.01,0.025,0.05,0.1", type="float", check=dict(min=0, max=1, max_num=10), ),
    dict(name="nrounds", chinese="最大迭代次数",description="最大迭代次数", multiple=True, default=10000, type="int", check=dict(min=10, max=50000, max_num=5), ),
    dict(name="early_stopping_rounds", chinese="指标阈值",description="该值为k时，表示若算法在验证集上连续k轮评价指标不变，则停止训练", multiple=True, default=100, type="int", check=dict(min=1, max=500, max_num=5), ),
    dict(name="subsample", chinese="实际训练样本占总比",description="实际训练样本占总样本比例", multiple=True, default=1, type="float", check=dict(min=0, max=1, max_num=5), ),
    dict(name="colsample_bytree", chinese="特征占总特征数的比例",description="每棵数所用的特征占总特征数的比例", multiple=True, default="0.8,1", type="float", check=dict(min=0, max=1, max_num=5), ),
    dict(name="max_depth", chinese="树的最大深度", multiple=True, default=6, type="int", check=dict(min=1, max=50, max_num=5), ),
    dict(name="min_child_weight", chinese="最小样本权重和",description="树的子节点进行分枝所需最小样本权重和", multiple=True, default=1, type="int", check=dict(min=0, max=100, max_num=5), ),
    dict(name="gamma", chinese="最小损失值", description="树的子节点进行分枝所需的最小损失值", multiple=True, default="0,0.1", type="float", check=dict(min=0, max=100, max_num=5), ),
    dict(name="nthread", chinese="线程数",description="线程数", multiple=True, default=1, type="int", check=dict(min=1, max=100, max_num=5), ),]),
    dict(name="lr",full_name="lr",chinese="lr",description="lr",params=[]),
    dict(name="svm",full_name="svm",chinese="svm",description="svm",params=[
    dict(name="C", chinese="惩罚项c的取值", description="惩罚项c的取值（惩罚因子大，则拒绝力度加大）", multiple=True, default="0.001,0.01,1,10,100,1000", type="float", check=dict(min=0, max=10000, max_num=10), ),
    dict(name="gamma", chinese="除去线性核外", description="除去线性核外，其他核的参数，默认为1/数据维数", multiple=True, default="0.001,0.01,0.1,1", type="float", check=dict(min=0, max=100, max_num=5), ),]),
    dict(name="nnet",full_name="nnet",chinese="nnet",description="nnet",params=[
    dict(name="size", chinese="隐层神经元个数", multiple=True, default="2,5", type="int", check=dict(min=0, max=100, max_num=10), ),
    dict(name="maxit", chinese="最大迭代次数", multiple=True, default="100,200,500,1000,5000", type="int", check=dict(min=10, max=10000, max_num=10), ),]),
    dict(name="cart",full_name="cart",chinese="cart",description="cart",params=[
    dict(name="minsplit", chinese="节点最小样本量",description="用于分枝的节点最小样本量", multiple=True, default="1,2,5,10", type="int", check=dict(min=1, max=100, max_num=10), ),
    dict(name="cp", chinese="复杂度参数的阈值",description="复杂度参数,决定是否进行剪枝的阈值", multiple=True, default="0.001,0.005,0.01", type="float", check=dict(min=0, max=1, max_num=5), ),]),
    dict(name="adaboost",full_name="adaboost",chinese="adaboost",description="adaboost",params=[
    dict(name="minsplit", chinese="最小样本量", description="树的子节点进行分枝所需最小样本量", multiple=True, default="5,10,15,20", type="int", check=dict(min=2, max=100, max_num=10), ),
    dict(name="cp", chinese="复杂度参数",description="复杂度参数", multiple=True, default="0.001,0.005,0.01", type="float", check=dict(min=0, max=1, max_num=5), ),
    dict(name="iter", chinese="迭代次数", description="迭代次数", multiple=True, default="50,100,200,300,400,500,1000", type="int", check=dict(min=10, max=10000, max_num=10), ),]),
    dict(name="naivebayes",full_name="naivebayes",chinese="naivebayes",description="naivebayes",params=[
    dict(name="laplace", chinese="平滑系数",description="平滑系数", multiple=True, default="0,0.1,1,5", type="float", check=dict(min=0, max=100, max_num=10), ),]),
    dict(name="lasso",full_name="lasso",chinese="lasso",description="lasso",params=[
    dict(name="alpha", chinese="正则化权重系数",description="正则化权重系数，alpha为L1的权重，1-alpha为L2的权重", multiple=True,default="0,0.25,0.5,0.75,1", type="float", check=dict(min=0, max=1, max_num=10), ),
    dict(name="lambda", chinese="正则化幅度", description="正则化幅度", multiple=True, default="0,0.01,0.1,0.5,1", type="float", check=dict(min=0, max=1, max_num=10), ),]),
    dict(name="mars",full_name="mars",chinese="mars",description="mars",params=[
    dict(name="degree", chinese="交叉程度",description="交叉程度", multiple=True, default="1,2,3", type="int", check=dict(min=1, max=10, max_num=5), ),
    dict(name="penalty", chinese="广义交叉验证惩罚项",description="每个节点的广义交叉验证惩罚项", multiple=True, default="0, 2, 5", type="float", param_list=[-1, 0, 5], check=dict(max_num=5), ),
    dict(name="newvar.penalty", chinese="惩罚值", description="前向传递过程中，每新增一个变量的惩罚值", multiple=True, default="0,0.01,0.2", type="float", check=dict(min=0, max=0.5, max_num=5), ),
    dict(name="fast.k", chinese="父节点个数最大值", description="前向传递每一步中，父节点个数最大值", multiple=True, default="0,10,20", type="int", check=dict(min=0, max=50, max_num=5), ),
    dict(name="fast.beta", chinese="老化系数",description="老化系数(ageingcoeffient)", multiple=True, default=0.1, type="float", check=dict(min=0, max=5, max_num=5), ),]),
    dict(name="auto",full_name="auto",chinese="auto",description="auto",params=[]),
]


# Explore通用参数
EXPLORE_COMMON_PARAMS = [
#     dict(name="data__filename",chinese="数据文件名",multiple=False,default=None,type="string",check=dict(max_num=1),description="",),
#     dict(name="dictionary__filename",chinese="字典文件名",multiple=False,default=None,type="string",check=dict(max_num=1,),description=""),
#     dict(name="id__varname", chinese="id变量名", multiple=False, default=None, type="string", check=dict(max_num=1),description=""),
#     dict(name="target__varname", chinese="目标变量名", multiple=False, default=None, type="string", check=dict(max_num=1),description=""),
    dict(name="miss.symbols", chinese="缺失值标记", multiple=True, default="NA,NULL,?", type="string", description = "缺失值标记",check=dict(max_num=10)),
    dict(name="quantiles",chinese="分位数",multiple=True,default="0,0.01,0.05,0.1,0.25,0.5,0.75,0.9,0.95,0.99,1",type="float",check=dict(min=0, max=1, max_num=21), description="分位数"),
    dict(name="sample_miss.cutoff", chinese="最大变量缺失比例阈值", multiple=False, default=0.99, type="float",check=dict(min=0, max=1,max_num=1), description="样本的最大变量缺失比例阈值，删除大于该比例的样本"),
    dict(name="variable_miss.cutoff", chinese="最大样本缺失比例阈值", multiple=False, default=0.99,type="float", check=dict(min=0, max=1,max_num=1), description="变量的最大样本缺失比例阈值，删除大于该比例的变量"),
    dict(name="variable_zero.cutoff", chinese="零值比例最大阈值", multiple=False, default=0.99,type="float", check=dict(min=0, max=1,max_num=1),description="变量的零值比例最大阈值，删除大于该比例的变量"),
    dict(name="max.nFactorLevels", chinese="变量最多因子数", multiple=False, default=1024,type="int", check=dict(min=10, max=1024,max_num=1),description="因子型变量最多因子数，删除因子类型大于该值的变量。当算法为rf时：max.nFactorLevels最大值不超过54,当算法为cart时：max.nFactorLevels最大值不超过52。"),
    dict(name="discretization", chinese="是否离散化", multiple=False, default=True, type="bool", check=dict(), description="是否离散化"),
    dict(name="nbins", chinese="变量离散化的分箱数", multiple=False, default=5, type="int",check=dict(min=3, max=20,max_num=1), description="数值变量离散化的分箱数"),
    dict(name="truncation.cutoff", chinese="数值变量最大截断值的阈值",multiple=False, default=10, type="float",check=dict(min=1, max=10, max_num=1), description="数值变量最大截断值的阈值，将大于该阈值和0.95分位数乘积的样本截断"),
    dict(name="breaks_zero.cutoff",chinese="是否数值变量分段统一",description="数值变量分段时，若零值比例大于该阈值，将所有零值单独归为一段",multiple=False,default=0.3,type="float",check=dict(min=0,max=1,max_num=1),),
    dict(name="iv.cutoff", chinese="根据iv删除变量",multiple=False, default=0.01, type="float",check=dict(min=0, max=0.1, max_num=1), description="iv最小阈值，删除iv值小于该阈值的变量；若为null，则不根据iv删除变量"),
    dict(name="collinearity.cutoff",chinese="共线性阈值",multiple=False, default=0.9, type="float",check=dict(min=0.3, max=1, max_num=1), description="共线性阈值,两个变量相关系数大于该阈值时，删除贡献较小的变量；若为null，则不根据相关系数删除变量"),
    dict(name="miss.imputation", chinese="进行缺失值填充", multiple=False,default=True, type="bool",check=dict(max_num=1), description="是否进行缺失值填充"),
    dict(name="unbalanced.cutoff",chinese="样本不平衡比例阈值", multiple=False,default=3, type="float",check=dict(min=1, max=10, max_num=1), description="样本不平衡比例阈值（多数/少数），用于欠抽样"),
    dict(name="onehot", chinese="进行one-hot",multiple=False, default=True, type="bool", check=dict(max_num=1),description="当选择如下算法时，onehot需设为True：'auto','xgb','svm','naivebayes','lasso'。"),
    dict(name="normalize", chinese="对变量进行标准化",multiple=False, default=True, type="bool",check=dict(max_num=1),description="当选择如下算法时，normalize需设为True：'nnet'。"),
    # dict(name="output__dir", chinese="输出文件夹名",multiple=False,type="string", check=dict(max_num=1)),

]


# Learn通用参数
LEARN_COMMON_PARAMS = [
    dict(name="metric",chinese="调参评价指标",multiple=False,default="ks",type="enum",param_list=['ks', 'auc'],check=dict(max_num=1),description="调参评价指标",),
    # dict(name="algorithm",chinese="算法名称",multiple=False,default="gbm",type="enum",param_list=['gbm', 'rf', 'xgb', 'lr', 'svm', 'nnet', 'cart', 'adaboost', 'naivebayes', 'lasso', 'mars', 'auto'],check=dict(max_num=1),description="算法名称",),
    # dict(name="hparms",chinese="参数组",multiple=False,default="NULL",type="list",param_list=["NULL",dict( name="ntree", chinese="数的棵数", default="3000", interaction="c(1,5,10,15,20)", type="int", check=dict(min=10, max=10000, max_num=10))],check=dict(max_num=1),description="参数组",),

    dict(name="prop.train", chinese="训练集比例", multiple=False, default=0.7, type="float",check=dict(min=0.5,max=1,max_num=1),description="训练集比例（另一部分为验证集）",),
    dict(name="nbins", chinese="模型验证时所用分箱数", multiple=False, default=20, type="int",check=dict(min=5,max=20,max_num=1),description="模型验证时所用分箱数",),
    dict(name="ncores", chinese="并行计算所用核数", multiple=False, default=None,type="int",check=dict(min=1,max=10,max_num=1),description="并行计算所用核数，NULL或者指定核数（视实际情况而定）",),
    # dict(name="output.dir", chinese="输出并行计算所用核数文件夹名", multiple=False, default=None, type="string",check=dict(max_num=1),description="",),

]



# Act通用参数
ACT_COMM_PARAMS=[
    dict(name="newdata.filename",chinese="预测数据文件名",description="预测数据文件名",multiple=True,type="string",check=dict(max_num=1,),),
    dict(name="reason_code.nvars",chinese="训练集的列数",description="用于进行reason code分析的变量个数", multiple=True,default=0,type="int",check=dict(max_num=1,),),
    dict(name="ncores",chinese="并行计算所用核数",description="并行计算所用核数",multiple=True,type="int",check=dict(min=1,max=10,max_num=1,),),
    dict(name="output.dir",chinese="输出文件夹名",description="输出文件夹名",multiple=True,type="string",check=dict(max_num=1,),),
]

# Test通用参数
TEST_COMM_PARAMS=[
    dict(name="test.data.filename",chinese="测试数据文件名",multiple=True,type="string",check=dict(max_num=1,),),
    dict(name="target.varname",chinese="目标变量名",multiple=True,type="string",check=dict(max_num=1,),),
    dict(name="output.dir",chinese="输出文件夹名",multiple=True,type="string",check=dict(max_num=1,),),
]

# Go 通用参数
GO_COMM_PARAMS=[
    dict(name="train.data.filename",chinese="训练数据文件名",multiple=True,type="string",check=dict(max_num=1,),),
    dict(name="dictionary.filename",chinese="字典文件名",multiple=True,type="string",check=dict(max_num=1,),),
    dict(name="test.data.filename",chinese="测试数据文件名",multiple=True,type="string",check=dict(max_num=1,),),
    dict(name="id.varname",chinese="id变量名",multiple=True,type="string",check=dict(max_num=1,),),
    dict(name="target.varname",chinese="训练集中目标变量名",multiple=True,type="string",check=dict(max_num=1,),),
    dict(name="target_test.varname",chinese="测试集中目标变量名",multiple=True,type="string",check=dict(max_num=1,),),
    dict(name="output.dir0",chinese="输出文件夹名",multiple=True,type="string",check=dict(max_num=1,),),

    dict(name="miss.symbols", chinese="缺失值标记", multiple=True, default="NA,NULL,?", type="string", description = ""),
    dict(name="quantiles",chinese="分位数",multiple=True,default="0,0.01,0.05,0.1,0.25,0.5,0.75,0.9,0.95,0.99,1",type="float",check=dict(min=0, max=1, max_num=21, description="")),
    dict(name="sample_miss.cutoff", chinese="样本的最大变量缺失比例阈值，删除大于该比例的样本", multiple=True, default=0.99, type="float",check=dict(min=0, max=1, max_num=1, description="")),
    dict(name="variable_miss.cutoff", chinese="变量的最大样本缺失比例阈值，删除大于该比例的变量", multiple=True, default=0.99,type="float", check=dict(min=0, max=1, max_num=1, description="")),
    dict(name="variable_zero.cutoff", chinese="变量的零值比例最大阈值，删除大于该比例的变量", multiple=True, default=0.99,type="float", check=dict(min=0, max=1, max_num=1, description="")),
    dict(name="max.nFactorLevels", chinese="因子型变量最多因子数，删除因子类型大于该值的变量", multiple=True, default=1024,type="int", check=dict(min=10, max=1024, max_num=1,description="当算法为rf时：max.nFactorLevels最大值不超过54,当算法为cart时：max.nFactorLevels最大值不超过52。")),
    dict(name="discretization", chinese="是否离散化", multiple=True, default=False, type="enum",param_list=[True, False], check=dict(max_num=1, description="'")),
    dict(name="nbins", chinese="数值变量离散化的分箱数", multiple=True, default=5, type="int",check=dict(min=3, max=20, max_num=1, description="'")),
    dict(name="truncation.cutoff", chinese="数值变量最大截断值的阈值，将大于该阈值和0.95分位数乘积的样本截断",multiple=False, default=10, type="float",check=dict(min=1, max=10, max_num=1), description=""),
    dict(name="breaks_zero.cutoff",chinese="数值变量分段时，若零值比例大于该阈值，将所有零值单独归为一段",description="",multiple=True,default="0.3",type="float",check=dict(min=0,max=1,max_num=1),),
    dict(name="iv.cutoff", chinese="iv最小阈值，删除iv值小于该阈值的变量；若为null，则不根据iv删除变量",multiple=True, default=0.01, type="float",check=dict(min=0, max=0.1, max_num=1), description=""),
    dict(name="collinearity.cutoff",chinese="共线性阈值,两个变量相关系数大于该阈值时，删除贡献较小的变量；若为null，则不根据相关系数删除变量",multiple=True, default=0.9, type="float",check=dict(min=0.3, max=1, max_num=1), description=""),
    dict(name="miss.imputation", chinese="是否进行缺失值填充", multiple=True,default=True, type="enum", param_list=[True, False],check=dict(max_num=1), description=""),
    dict(name="unbalanced.cutoff",chinese="样本不平衡比例阈值（多数/少数），用于欠抽样", multiple=True,default=3, type="float",check=dict(min=1, max=10, max_num=1), description=""),

    dict(name="algorithm.library",chinese="算法库", multiple=True,default="'gbm', 'rf', 'xgb', 'lr', 'svm', 'nnet', 'cart', 'adaboost', 'naivebayes', 'lasso', 'mars', 'auto'", type="string",param_list=['gbm', 'rf', 'xgb', 'lr', 'svm', 'nnet', 'cart', 'adaboost', 'naivebayes', 'lasso', 'mars', 'auto'],check=dict( max_num=12), description="算法库"),

    dict(name="metric", chinese="调参评价指标", multiple=False, default="ks", type="enum", param_list=['ks', 'auc'],check=dict(max_num=1), description="调参评价指标", ),
    dict(name="reason_code.nvars",chinese="reason code分析变量数",multiple=True,default=0,type="int",check=dict(max_num=1,),description="用于进行reason code分析的变量个数"),
    dict(name="ncores", chinese="并行计算所用核数", multiple=False, default=None, type="int", check=dict(min=1,max=10,max_num=1),description="NULL或者指定核数（视实际情况而定）", ),

]
