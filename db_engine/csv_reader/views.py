# -*- coding:utf-8 -*-

# from django.http import JsonResponse

from django.shortcuts import render
# from django.shortcuts import get_object_or_404, redirect, get_list_or_404
from django.views.generic.list import ListView
# from django.views.generic.detail import DetailView
# import markdown
# import os
# import re
import logging
# from setting import WORKING_DIRECTORY
from . import csv_reader


logger = logging.getLogger(__name__)

class IndexView(ListView):
    template_name = 'index.html'
    # 制定获取的model数据列表的名字

    # csv上传文件
    def uploadCsvReaderInfoType(request):
        response = csv_reader.upload(request)
        return response

    # csv字段类型修改
    def updateCsvReaderInfoType(request):
        response = csv_reader.update(request)
        return response

    def saveCsvReaderInfo(request):
        response = csv_reader.saveInfo(request)
        return response

    def loadFieldType(request):
        response = csv_reader.load_field_type(request)
        return response

    def loadinfo(request):
        response = csv_reader.load_info(request)
        return response


    # learn加载获取参数
    def queryFields(self,request):
        # return render(request,IndexView.template_name)
        return render(request,IndexView.template_name)

    def ajax(request):
        import time
        current_time = time.time()
        return render(request, 'ajax.html', {'current_time': current_time})

    def upLoad(request):
        if request.method == 'POST':
            ret = {'status': False, 'data': None, 'error': None}
            request.POST.get('file')



