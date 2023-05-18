import logging

from datetime import timedelta

import celery

from celery.signals import after_setup_logger


class TaskError(Exception):
    ...


class TaskFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from celery._state import get_current_task

            self.get_current_task = get_current_task
        except ImportError:
            self.get_current_task = lambda: None

    def format(self, record: logging.LogRecord) -> str:
        task = self.get_current_task()
        attributes: list[str] = [
            "task_name",
            "task_id",
        ]
        for a in attributes:
            record.__dict__.setdefault(a, "")
        if task and task.request:
            record.__dict__.update(
                task_id=task.request.id,
                task_name=task.name,
            )
        return super().format(record)


class BaseTask(celery.Task):
    autoretry_for = (TaskError,)
    default_retry_delay = timedelta(seconds=30).seconds
    retry_kwargs = {"max_retries": 3}
    ignore_result = False
    max_retries = 3
    retry_backoff = True
    retry_backoff_max = timedelta(minutes=10).seconds
    retry_jitter = True

    def run(self, *args, **kwargs):
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


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    handler = logging.StreamHandler()
    handler.setFormatter(
        TaskFormatter(
            fmt=(
                "[{asctime}] {name} ({levelname}) - {task_id} - {task_name} - {message}"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{",
        )
    )
    logger.setLevel(logging.INFO)
    logger.handlers = []
    logger.propagate = False
    logger.addHandler(handler)


app.autodiscover_tasks()
