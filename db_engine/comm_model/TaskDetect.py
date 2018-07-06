import logging

from comm_model.apps import ExecutionStatus, PENDING
from comm_model.components.AtomAct import AtomAct
from comm_model.components.AtomCommon import extract_component_type
from comm_model.components.AtomExplore import AtomExplore
from comm_model.components.AtomLearn import AtomLearn
from comm_model.components.AtomTest import AtomTest
from comm_model.components.FeatureCombine import FeatureCombine
from comm_model.components.RobotX import RobotX
from comm_model.models import Execution, Task
from csv_reader.models import CsvReaderInfo

logger = logging.getLogger("monitor")


def task_detect():
    executions = Execution.objects.filter(status=ExecutionStatus.RUNNING) # type: list[Execution]
    executions = [ec.task_id for ec in executions]
    tasks = Task.objects.filter(task_status=PENDING, relies=0, task_id__in=executions)
    for task in tasks:
        project_id = task.project_id
        component_id = task.component_id
        task_id = task.task_id
        component_type = extract_component_type(component_id)
        executor_class = eval(component_type)
        executor = executor_class(project_id, component_id)
        executor.execute(task_id)
        logger.info("%s-%s-%s submitted to task queue" %(project_id, component_id, task_id))
        print("-----------------------------------------------------------------------")


if __name__ == "__main__":
    # 引用eval()类型
    AtomTest()
    FeatureCombine()
    RobotX()
    AtomLearn()
    AtomAct()
    AtomExplore()
    CsvReaderInfo()
    CsvReaderInfotype()