import sys, os, django

sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])))
os.environ['DJANGO_SETTINGS_MODULE'] = 'databrain.settings'
django.setup()


from comm_model.components.AtomExplore import AtomExplore

AtomExplore.TASK_RELY.delay(project_id='13', component_id='AtomExplore3', task_id="13_0")