from __future__ import print_function
import sys
from datetime import date, timedelta  # pylint: disable=E0611
from time import sleep  # pylint: disable=E0611

from django.core.management import call_command
from django.core.management.base import BaseCommand
from djcelery.models import TaskMeta


class Command(BaseCommand):
    """This commands periodically cleans up data that accumulates when OIOIOI
       is running.
    """
    SESSION_CLEAR_INTERVAL = 60 * 60 * 24 * 5  # 5 days
    CELERY_TASKMETA_EXPIRY = 7  # 7 days

    def handle(self, *args, **options):
        while True:
            # Clear django sessions
            call_command('clearsessions')
            # Clear django-celery data
            d = date.today() - timedelta(days=self.CELERY_TASKMETA_EXPIRY)
            TaskMeta.objects.filter(date_done__lt=d).delete()

            print('Performed cleanup on ' + str(date.today()), file=sys.stderr)
            sleep(self.SESSION_CLEAR_INTERVAL)
