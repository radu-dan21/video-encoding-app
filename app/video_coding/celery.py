from datetime import timedelta
from typing import Any

import celery

from celery.signals import setup_logging


class TaskError(Exception):
    ...


class BaseTask(celery.Task):
    """
    Custom Celery base Task class used throughout the project
    """

    autoretry_for = (TaskError,)
    default_retry_delay = timedelta(seconds=30).seconds
    retry_kwargs = {"max_retries": 3}
    ignore_result = False
    max_retries = 3
    retry_backoff = True
    retry_backoff_max = timedelta(minutes=10).seconds
    retry_jitter = True

    def run(self, *args, **kwargs) -> Any:
        return super().run(*args, **kwargs)


app = celery.Celery(
    "video_coding",
    task_cls=BaseTask,
    imports=["video_coding.tasks"],
    worker_enable_remote_control=False,
)

app.config_from_object(
    "video_coding.settings:Celery",
    silent=False,
    force=True,
    namespace=None,
)


@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig  # noqa

    from django.conf import settings  # noqa

    dictConfig(settings.LOGGING)


app.autodiscover_tasks()
