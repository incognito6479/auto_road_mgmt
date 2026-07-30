# config package

# Ensures the Celery app is loaded whenever Django starts, so `@shared_task`
# always has an app to bind to.
from .celery import app as celery_app

__all__ = ("celery_app",)
