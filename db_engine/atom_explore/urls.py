from django.conf.urls import url

from atom_explore import views

urlpatterns = [
    url(r'saveInfoDefualt$', views.saveInfoDefualt, name='saveInfoDefualt$'),
    url(r'saveInfo$', views.saveInfo, name='saveInfo$'),
    url(r'load$', views.load, name='load$'),
    url(r'load_params$', views.load_list, name='load_list$'),
]