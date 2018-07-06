from django.conf.urls import url
from atom_act import views

urlpatterns = [
    url(r'saveInfo$', views.saveInfo),
    url(r'load$', views.load),
    # url(r'download_prediction$', views.download_prediction),
    # url(r'report$', views.report),
    # url(r'reportFiles$', views.reportFiles),
]