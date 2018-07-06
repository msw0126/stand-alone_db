import copy
import datetime
import os
import pickle
from abc import ABCMeta, abstractmethod

import setting
from comm_model import apps
from comm_model.apps import COMPONENTS
from comm_model.components.AtomCommon import extract_component_type
from comm_model.models import Task, TaskRelies
from common.UTIL import mk_working_directory

FULL_EXECUTION = 'FULL_EXECUTION'
EXECUTABLE = [COMPONENTS.ROBOTX,COMPONENTS.FEATURE_COMBINE,COMPONENTS.ATOM_LEARN,COMPONENTS.ATOM_ACT,COMPONENTS.ATOM_TEST,COMPONENTS.ATOM_EXPLORE]
CONT_EXECUTION = 'CONT_EXECUTION'
SING_EXECUTION = 'SING_EXECUTION'

class Param(object):
    def __init__(self, name, values):
        self.name = name
        self.values = values


class ParamCheckingError(object):
    def __init__(self, name, error):
        self.name = name
        self.error = error


class Point:
    def __init__(self, id=None):
        self.relies = set()
        self.forwards = set()
        self.id = id
        self.relies_bak = set() # type: set[Point]
        if id is not None:
            self.type = extract_component_type(id)

    def add_rely(self, rely):
        self.relies.add(rely)

    def remove_rely(self, rely, bag: set):
        if rely in self.relies:
            self.relies.remove(rely)
        if len(self.relies) == 0:
            bag.add(self)

    def shoot(self, bag):
        for point in self.forwards:
            assert isinstance(point, Point)
            point.remove_rely(self, bag)

    def add_forward(self, forward):
        self.forwards.add(forward)

    def __repr__(self):
        return str(self.id)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.id == other
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class Toplogy:
    def __init__(self):
        self.points = dict()  # type: dict[str, Point]
        self.levels = None # type: list[set[Point]]

    def add_line(self, start, end):
        if start not in self.points:
            point = Point(start)
            self.points[start] = point
        if end not in self.points:
            point = Point(end)
            self.points[end] = point

        end_point = self.points[end]
        start_point = self.points[start]
        start_point.add_forward(end_point)
        end_point.add_rely(start_point)

    def sort(self):
        for point in self.points.values():
            point.relies_bak = copy.copy(point.relies)
        self.levels = list()
        remove = set()
        remove.add(Point())
        while len(self.points)>0:
            current_level = set()
            for point in self.points.values():
                for  removed_point in remove:
                    point.remove_rely(removed_point, current_level)
            for point in current_level:
                del self.points[point.id]
            remove = current_level
            self.levels.append(current_level)

    def get_previous_component(self, point_id):
        levels = copy.copy(self.levels)
        level_of_point = None
        for idx,level in enumerate(levels):
            if level_of_point is None:
                if point_id in level:
                    level_of_point = idx
                    break
                else:
                    continue
        if level_of_point == None:
            level_of_point = 0
        levels = levels[:level_of_point+1]
        top_point = None
        for p in levels[level_of_point]:
            if p.id == point_id:
                top_point = p
                break
        levels[level_of_point] = [top_point]
        idx = level_of_point-1
        high_level = set()
        while idx >= 0:
            new_level = set()
            high_level |= set(levels[idx+1])
            for point in levels[idx]:
                if len(point.forwards&high_level)>0:
                    new_level.add(point)
            levels[idx] = list(new_level)
            idx -= 1
        high_level |= set(levels[idx+1])
        # 移除要执行节点
        high_level.remove(levels[level_of_point][0])
        return levels, high_level


class ExecutionQuery(object):
    def __init__(self, status, start_time, end_time):
        self.status = status
        self.start_time = start_time
        self.end_time = end_time
        self.detail = list()

    def add_detail(self, component_id, task_status, detail, error_code, application_id, tracking_url, has_log,
                   start_time, end_time):
        self.detail.append(dict(
            component_id=component_id,
            task_status=task_status,
            error_code=error_code,
            application_id=application_id,
            tracking_url=tracking_url,
            detail=detail,
            has_log=has_log,
            start_time=start_time,
            end_time=end_time
        ))



class Component(object):
    __metaclass__ = ABCMeta

    PREVIOUS = "PREVIOUS.PKL"

    YARN_LOG_NAME = "LOG.HEX"

    COMPONENT_TYPE = None

    TASK_RELY = None

    # DEFAULT_DRIVER_MEMORY = setting.DEFAULT_DRIVER_MEMORY
    #
    # DEFAULT_NUM_EXECUTORS = setting.DEFAULT_NUM_EXECUTORS
    #
    # DEFAULT_EXECUTOR_MEMORY = setting.DEFAULT_EXECUTOR_MEMORY

    def __init__(self, project_id, component_id):
        self.project_id = project_id
        self.component_id = component_id
        self.loaded = False

    def need_execution(self, force=False):
        changed = True if force else self.changed()
        if changed:
            if not self.loaded:
                self.load_from_db()
            pickle_path = mk_working_directory(self.project_id, self.component_id, Component.PREVIOUS)
            with open(pickle_path, 'wb') as f:
                pickle.dump(self, f)
            self.prepare()
        return changed

    def execute(self, task_id):
        res = self.TASK_RELY.delay(project_id=self.project_id, component_id=self.component_id, task_id= task_id)
        # 记录任务提交时间
        submit_time = datetime.datetime.now()
        Task.objects.filter(project_id=self.project_id, component_id=self.component_id) \
            .update(submit_time=submit_time, task_status=apps.SUBMITTED, celery_id=res.id)

    def record(self, task_id, relies, forwards):
        record_time = datetime.datetime.now()
        Task.objects.update_or_create(project_id=self.project_id,
                                      component_id=self.component_id,
                                      defaults=dict(
                                          task_id=task_id,
                                          component_type=self.COMPONENT_TYPE,
                                          error_code=None,
                                          application_id=None,
                                          tracking_url=None,
                                          has_log=False,
                                          task_status=apps.PENDING,
                                          relies=relies,
                                          submit_time=None,
                                          record_time=record_time,
                                          detail=None,
                                          start_time=None,
                                          end_time=None
                                      )
                                      )
        # 保存依赖关系
        if forwards is not None:
            task_relies = list()
            for forward in forwards:
                task_relies.append(
                    TaskRelies(project_id=self.project_id, sc_comp_id=self.component_id, tg_comp_id=forward))
            TaskRelies.objects.bulk_create(task_relies)

    def changed(self):
        project_id = self.project_id
        component_id = self.component_id
        previous_pickle_path = os.path.join(setting.WORKING_DIRECTORY, project_id, component_id, self.PREVIOUS)
        if not os.path.exists(previous_pickle_path):
            return True
        # 查询之前执行状态
        previous_execute_task = Task.objects.filter(project_id=self.project_id, component_id=self.component_id)
        if len(previous_execute_task) == 0:
            return True
        previous_execute_task = previous_execute_task[0]
        assert isinstance(previous_execute_task, Task)
        if previous_execute_task.task_status != apps.SUCCEEDED:
            return True
        with open(previous_pickle_path, 'rb') as f:
            previous_component = pickle.load(f)
            self.load_from_db()
            return not self == previous_component

    # def evaluate_resource(self):
    #     return self.DEFAULT_DRIVER_MEMORY, self.DEFAULT_NUM_EXECUTORS, self.DEFAULT_EXECUTOR_MEMORY

    def load_from_db(self):
        """
        load configuration from database
        :return:
        """
        self.__load_from_db__()
        self.loaded = True

    @abstractmethod
    def __load_from_db__(self):
        """
        load configuration from database
        :return:
        """
        pass

    @abstractmethod
    def prepare(self):
        """
        prepare configuration files
        :return:
        """
        pass

    @staticmethod
    def get_yarn_log_path(project_id, component_id):
        return mk_working_directory(project_id, component_id, Component.YARN_LOG_NAME)

    @staticmethod
    def fetch_log(project_id, component_id):
        yarn_log_path = Component.get_yarn_log_path(project_id, component_id)
        logs = list()
        with open(yarn_log_path, "rb") as f:
            t_logs = f.readlines()
            for line in t_logs:
                try:
                    logs.append(line.decode("utf-8"))
                except Exception: pass
        return "".join(logs)

    @staticmethod
    def cluster_working_directory(project_id, component_id, *external):
        return "%s/%s/%s" %(setting.WORKING_DIRECTORY, project_id, component_id)

    def check_config(self,last_component_id):
        pass

