# import copy
# import json
# from collections import OrderedDict
#
# import setting
# from test1 import __orderd_dict__
#
# LEARN_COMMON_PARAMS = [
#     dict(name="prop.train", chinese="训练集比例（另一部分为验证集）", multiple=True, default="0.7", type="float",check=dict(mix=0.5,max=1,max_num=1),description="",),
#     dict(name="nbins", chinese="模型验证时所用分箱数", multiple=False, default="20", type="int",check=dict(mix=5,max=20,max_num=1),description="",),
#     dict(name="ncores", chinese="并行计算所用核数", multiple=False, default=None, type="int",check=dict(max_num=1),description="NULL或者指定核数（视实际情况而定）",),
#     dict(name="output.dir", chinese="输出文件夹名", multiple=False, default=None, type="string",check=dict(max_num=1),description="",),
# ]
#
#
#
# COMM_PARAMS = {
#     params['name'] : params
#     for params in setting.EXPLORE_COMMON_PARAMS
# }
#
# # ALGORITHM_PARAMS = {
# #     key: __orderd_dict__(params)
# #     for key, params in COMM_PARAMS.items()
# # }
#
# # print(ALGORITHM_PARAMS)
#
#
# import os
# BASE_DIR = os.path.dirname(os.path.join("sdf","sdf")) #获取当前文件夹的父目录绝对路径
# print(BASE_DIR)
# import os,sys,django
# sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])))
# os.environ["DJANGO_SETTINGS_MODULE"] = "databrain.settings"
# django.setup()
# from comm_model.components.RobotX import Method
# from common.UTIL import to_json
#
# me1 = Method()
# me1.add_summary_method("sum")
# me1.add_summary_method("avg")
# me1.add_summary_method("max")
# me1.add_summary_method("min")
#
# print(to_json(me1))



def getDate():
    import datetime
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d%H%M%S')
# while(1):
#     with open("~/aaa.txt", 'w', encoding='utf-8') as f:
#         f.write(getDate())
#     from time import sleep
#     sleep(1)

aa=['target','aaa']
[item.capitalize() for item in aa]
if "Target" in [item.capitalize() for item in aa]:
    print("aaaaa")