from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import sys, os, django

logger = logging.getLogger("monitor")

sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])))
# os.environ['DJANGO_SETTINGS_MODULE'] = 'databrain.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "databrain.settings")
django.setup()
from comm_model.TaskDetect import task_detect



logger.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
scheduler = BlockingScheduler(daemonic=True)
scheduler.add_job(task_detect, 'interval', seconds=5)
try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    # Not strictly necessary if daemonic mode is enabled but should be done if possible
    scheduler.shutdown()
    logger.info('Exit The Job!')
