from django.conf.urls import url

from comm_model import views

urlpatterns = [
    url(r'get_id$', views._get_id),
    url(r'execute$', views._execute),
    url(r'queryLog$', views._queryLog),

    url(r'status$', views._execution_status),
    url(r'current_exec$', views._current_execution),
    url(r'get_log$', views._get_log),
    url(r'kill_task$', views._kill_task),
    url(r'stop_all$', views._stop_all),
    
    url(r'delete$', views._delete),

    url(r'report$', views.report),
    url(r'reportFiles$', views.reportFiles),
    url(r'downLoadReportZip*', views.downLoadReportZip),

]