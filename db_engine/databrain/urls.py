"""databrain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from comm_model import components
from common import xml

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # 公用组件
    url(r'^xml/save$', xml.save),
    url(r'^xml/load$', xml.load),

    url(r'^components/', include('comm_model.urls')),

    url(r'^csv_reader/', include('csv_reader.urls')),
    url(r'^atom_learn/', include('atom_learn.urls')),
    url(r'^atom_explore/', include('atom_explore.urls')),
    url(r'^atom_act/', include('atom_act.urls')),
    url(r'^atom_test/', include('atom_test.urls')),
    url(r'^robot_x/', include('robot_x.urls')),

]
