from django.conf.urls import url
from robot_x import views

urlpatterns = [

    url(r'save_container$', views.save_container),
    url(r'save_relation$', views.save_relation),
    url(r'delete_relation$', views.delete_relation),
    url(r'load_configuration$', views.load_configuration),
    url(r'save_xml$', views.save_xml),
    url(r'load_xml$', views.load_xml),
    url(r'load_container_fields$', views.container_fields),

]
