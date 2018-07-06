from django.conf.urls import url
from django.views.generic.list import ListView
from . import views

class IndexView(ListView):

    def algorithmList(request):
        return views.load_list(request)

    def algorithmInfo(request):
        return views.load_list_params(request)

    def saveInfoDefualt(request):
        return views.save_with_default(request)

    def saveInfo(request):
        return views.saveInfo(request)

    def load(request):
        return views.load(request)


urlpatterns = [
    url(r'algorithmList$', IndexView.algorithmList, name='algorithmList$'),
    url(r'algorithmInfo$', IndexView.algorithmInfo, name='algorithmInfo$'),
    url(r'saveInfoDefualt$', IndexView.saveInfoDefualt, name='saveInfoDefualt$'),
    url(r'saveInfo$', IndexView.saveInfo, name='saveInfo$'),
    url(r'load$', IndexView.load, name='load$'),
    # url(r'update$', IndexView.updateCsvReaderInfoType, name='update$'),
    # url(r'saveInfo$', IndexView.saveCsvReaderInfo, name='saveInfo'),
    # url(r'query_fields$', views.IndexView.queryFields, name='queryFields'),
]