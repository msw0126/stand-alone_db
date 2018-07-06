import os
import sys
import hashlib
import re
import inspect
import json
from datetime import datetime

from django.contrib import auth
from django.core.paginator import Paginator
from django.http import HttpResponse
from py4j.protocol import Py4JNetworkError, Py4JJavaError
from setting import DEVELOP_MODE, DEVELOP_ACCOUNT, DEVELOP_PASSWD

from common.ERRORS import PARAMETER_MISSING_ERROR, GET_DENIED_FOR_THIS_METHOD, NOT_LOGIN, PY4J_CONNECTION_ERROR
import typing
from setting import WORKING_DIRECTORY
# sys.setrecursionlimit(10000)
sys.setrecursionlimit(2000)
class Response(object):
    """
    通用返回类型
    成功，返回 数据
    失败，返回 错误码，错误细节
    """

    def __init__(self, error_code, detail):
        if error_code is not None:
            self.error_code = error_code
        self.detail = detail

    def __call__(self, *args, **kwargs):
        return HttpResponse(self.__to_json__(), content_type="application/json")

    @classmethod
    def success(cls, detail=None):
        return Response(None, detail)()

    @classmethod
    def fail(cls, error_code, detail=None):
        return Response(error_code, detail)()

    def __to_json__(self):
        return to_json(self)

def to_json(obj, indent=0):
    """
    json格式化
    """
    obj_t = __trans_to_ser__(obj)
    return json.dumps(obj_t, indent=indent)


def __trans_to_ser__(obj):
    if hasattr(obj, '__dict__'):
        return __trans_to_ser__(obj.__dict__)
    elif isinstance(obj, list):
        obj_n = list()
        for v in obj:
            obj_n.append(__trans_to_ser__(v))
        return obj_n
    elif isinstance(obj, dict):
        obj_n = dict()
        for k, v in obj.items():
            obj_n[k] = __trans_to_ser__(v)
        return obj_n
    elif isinstance(obj, set):
        obj_n = list()
        for v in obj:
            obj_n.append(__trans_to_ser__(v))
        return obj_n
    elif isinstance(obj, datetime):
        return str(obj)
    else:
        return obj


GET_NOT_ALLOWED = Response.fail(GET_DENIED_FOR_THIS_METHOD)
NO_DETAIL_SUCCESS = Response.success()
NOT_LOGIN_RESPONSE = Response.fail(NOT_LOGIN)
PY4J_CONNECTION_ERROR_RESPONSE = Response.fail(PY4J_CONNECTION_ERROR)


def auto_param(post_only=False):
    def auto_param_decorator(func):
        def wrapper(*arg, **kwargs):
            request = arg[0]
            if request.method == 'GET' and post_only:
                return GET_NOT_ALLOWED

            if request.method == 'GET':
                param_getter = request.GET
            else:
                # POST请求中，如果有文件，需要把文件也放入字典
                param_getter = request.POST
                files = request.FILES
                if len(files) > 0:
                    param_getter = dict()
                    for field_name, value in request.POST.items():
                        param_getter[field_name] = value
                    for field_name, file in files.items():
                        param_getter[field_name] = file
            params = inspect.signature(func).parameters

            missing_params = []
            type_error_params = []
            if len(params) != 1:
                for idx, param in enumerate(params):
                    if idx == 0: continue
                    if param == 'user_pk':
                        kwargs[param] = request.user.id
                        continue
                    describe = params.get(param)
                    parameter_setting(param, describe, param_getter, missing_params, type_error_params, kwargs)
            if len(missing_params) > 0:
                resp = Response.fail(PARAMETER_MISSING_ERROR, "missing param: %s" % ",".join(missing_params))
                return resp
            return func(*arg, **kwargs)

        return wrapper
    return auto_param_decorator


def login_required(func):
    def wrapper(*arg, **kwargs):
        request = arg[0]
        if DEVELOP_MODE:
            # develop mode support
            user = auth.authenticate(username=DEVELOP_ACCOUNT, password=DEVELOP_PASSWD)
            auth.login(request, user)
            return func(*arg, **kwargs)
        if request.user.is_authenticated():
            return func(*arg, **kwargs)
        return NOT_LOGIN_RESPONSE
    return wrapper


def parameter_setting(param, describe, param_getter, missing_params, type_error_params, kwargs):
    annotation = describe.annotation
    if param in param_getter:
        value = param_getter[param]
        if isinstance(annotation, type):
            try:
                value = annotation(value)
            except Exception as e:
                type_error_params.append("%s expect %s get %s" %(param, str(annotation), value))
        kwargs[param] = value
    elif isinstance(annotation, typing.GenericMeta) and "typing.List" in str(annotation):
        subclass = annotation.__args__[0] if hasattr(annotation,'__args__') else annotation.__parameters__[0]
        obj_map = dict()
        if subclass == str or subclass == int:
            param_list_key = "%s[]" % param
            if param_list_key in param_getter:
                kwargs[param] = param_getter.getlist(param_list_key)
            elif describe.default == inspect._empty:
                missing_params.append(param)
        elif hasattr(subclass, '__init__'):
            reg = re.compile('%s\[(\d+)\]\[([\w_][\w\d_]*)\]' % param)
            for k, v in param_getter.items():
                finds = re.findall(reg, k)
                if len(finds) != 1 or len(finds[0]) != 2:
                    continue
                idx = int(finds[0][0])
                param_name = finds[0][1]
                if idx not in obj_map:
                    obj_map[idx] = dict()
                obj_map[idx][param_name] = v
            kwargs[param] = [subclass(**obj_map[idx]) for idx in sorted(obj_map.keys())]
        else:
            missing_params.append(param)
    elif describe.default == inspect._empty:
        # 如果参数没有默认值，标记为传参错误
        missing_params.append(param)


def mk_working_directory(project_id ,component_id, *external_path):
    component_directory = os.path.join(WORKING_DIRECTORY, project_id, component_id)
    if not os.path.exists(component_directory):
        os.makedirs(component_directory)
    return os.path.join(component_directory, *external_path)


def py4j(java_function, *args):
    try:
        result = java_function(*args)
        return result
    except Py4JNetworkError as e:
        return PY4J_CONNECTION_ERROR_RESPONSE
    except Py4JJavaError as e:
        # 查询出错，返回错误信息
        raise e


def page(model_cls, transform, page_num, key_word_param=None, page_size=20):
    """
    get particular page of objects
    :param transform: transform method for result
    :param model_cls: model class
    :param page_num: page num
    :param key_word_param: key word
    :param page_size: page size
    :return: object list
    """
    if key_word_param is None:
        objects = model_cls.objects.all()
    else:
        objects = model_cls.objects.filter(**key_word_param)

    pager = Paginator(objects, page_size)
    if page_num <= 0:
        page_num = 0
    elif page_num > pager.num_pages:
        page_num=pager.num_pages

    objects = list()
    for obj in pager.page(page_num).object_list:
        objects.append(transform(obj))
    return dict(
        total_pages=pager.num_pages,
        page_size=page_size,
        page_num=page_num,
        datas=objects
    )


def model_transform(model_object):
    """
    transform django model object to dict
    :param model_object: model object
    :return: dict
    """
    attribute_dict = dict()
    for p,v in model_object.__dict__.items():
        if v is None or isinstance(v,int) or isinstance(v, float) or isinstance(v, str) or isinstance(v, bool):
            attribute_dict.setdefault(p, v)
        elif isinstance(v, datetime):
            attribute_dict.setdefault(p, str(v))
    return attribute_dict


def md5(*args):
    args_str = "_".join([str(arg) for arg in args])
    m = hashlib.md5()
    m.update(args_str.encode())
    return m.hexdigest()


# copy by
DATE_MAPPING = {
    7 : (r"^\d\d{3}-[0-1]\d$", "month"),
    10: (r"^\d\d{3}-[0-1]\d-[0-3]\d$", "day"),
    13: (r"^\d\d{3}-[0-1]\d-[0-3]\d [0-2]\d$", "hour"),
    16: (r"^\d\d{3}-[0-1]\d-[0-3]\d [0-2]\d:[0-6]\d$", "minute"),
    19: (r"^\d\d{3}-[0-1]\d-[0-3]\d [0-2]\d:[0-6]\d:[0-6]\d$","second")
}

def is_date(sample_data):
    none_count = 0
    fmt = None
    rep = None
    for sample in sample_data:
        if sample is None:
            none_count += 1
            continue
        if len(sample) not in DATE_MAPPING:
            return False, None
        rep_, fmt_ = DATE_MAPPING[len(sample)]
        if rep is None:
            rep = rep_
            fmt = fmt_
        if fmt != fmt_:
            return False, None
        matched = re.match(rep_, sample, flags=0)
        if matched is None:
            return False, None
    if none_count == len(sample_data):
        return False, None
    return True, fmt



def excute_before():
    def auto_param_decorator(func):
        def wrapper(*arg, **kwargs):
            need_execute = arg[0]
            project_id = arg[1]
            type_error_params = []

            # if len(arg) != 0:
            #     raise Exception("任务开始执行失败: %s" % ",".join(type_error_params))
                # resp = Response.fail(PARAMETER_MISSING_ERROR, "执行失败: %s" % ",".join(type_error_params))
                # return resp
            return func(*arg, **kwargs)
        return wrapper
    return auto_param_decorator
