import subprocess
import sys, os, django

import setting

sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])))
os.environ['DJANGO_SETTINGS_MODULE'] = 'databrain.settings'
django.setup()

from comm_model import apps
from comm_model.tasks import update_task_detail, local_submit

task_id = 12
partial_command = setting.ROBOTX_PATH
command = partial_command ,\
        "--config_path", "E:/your/dir/static/27/RobotX4/robotx_config.json",\
        "--output", "E:/your/dir/static/27/RobotX4",\
        "--dict_only n",\
        "--dbname ","testdb%s"%task_id,"--delete_db y","--label ","robot_x_%s"%task_id

print(" ".join(command))
status = None
try:
    p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    status = local_submit("1", "1", task_id, p)
except Exception as e:
    update_task_detail("1", "1", task_id, detail=str(e))
    print(apps.FAILED)
print(status)