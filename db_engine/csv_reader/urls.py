from django.conf.urls import url

from .views import IndexView

# app_name = 'csvreader'
urlpatterns = [
    url(r'upload$', IndexView.uploadCsvReaderInfoType, name='upload$'),
    url(r'update$', IndexView.updateCsvReaderInfoType, name='update$'),
    url(r'saveInfo$', IndexView.saveCsvReaderInfo, name='saveInfo'),
    url(r'loadFieldType$', IndexView.loadFieldType, name='loadFieldType'),
    url(r'loadInfo$', IndexView.loadinfo, name='loadinfo'),
]