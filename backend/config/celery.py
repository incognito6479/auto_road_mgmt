"""
Celery app for the project. Broker/backend and schedule come from
`config.settings` (CELERY_* keys), same env-driven pattern as the rest of
the Django config.
"""

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Runs once a day, shortly after midnight — groups whose ends_at has
    # already passed get marked finished and their students moved off
    # "enrolled" for that group.
    "finish-expired-groups-daily": {
        "task": "management.tasks.finish_expired_groups",
        "schedule": crontab(hour=0, minute=5),
    },
}
