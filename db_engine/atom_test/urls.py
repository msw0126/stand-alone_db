from django.conf.urls import url
from atom_test import views

urlpatterns = [
    url(r'saveInfo$', views.save),
    url(r'load$', views.load),

    # url(r'download_prediction$', views.download_prediction),
    # url(r'report$', views.report),
]