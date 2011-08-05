import datetime
import imp
import logging
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from emtools.emadmin.models import Schedule

log = logging.getLogger('schedule')

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Taken from admin
        transaction.enter_transaction_management()
        transaction.managed(True)
        threads = []
        for app in settings.INSTALLED_APPS:
            try:
                last_element = app.split('.')[-1]
                app_path = __import__(app, {}, {}, [last_element]).__path__
            except AttributeError:
                continue
            try:
                imp.find_module('schedule', app_path)
            except ImportError:
                continue
            transaction.commit()
            try:
                m = __import__("%s.schedule" % app, fromlist=["SCHEDULE"])
                for name, function, delay_in_minutes in m.SCHEDULE:
                    now = datetime.datetime.utcnow()
                    obj, created = Schedule.objects.get_or_create(
                        name=name,
                        defaults={
                            'last_run': now
                            })
                    delay = datetime.timedelta(minutes=delay_in_minutes)
                    last_run = obj.last_run
                    next_run = last_run + delay
                    if created or now >= next_run:
                        # Skip missed time slices
                        while now >= last_run + delay:
                            last_run += delay
                        obj.last_run = last_run
                        obj.next_run = last_run + delay
                        obj.save()
                        transaction.commit()
                        function()
                    else:
                        transaction.commit()
            except Exception as e:
                transaction.rollback()
                log.error("Error in scheduling %s: %s" % (
                        app,
                        traceback.format_exc()))
        transaction.leave_transaction_management()
