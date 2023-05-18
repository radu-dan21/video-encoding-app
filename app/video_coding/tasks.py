import logging

from celery import shared_task
from video_coding.entities.models import VideoEncoding


logger = logging.getLogger(__name__)


@shared_task(queue="web")
def test():
    logger.info("!!! HEY !!!!")


@shared_task(queue="web")
def test_db():
    VideoEncoding.objects.create(name="CELERY", ffmpeg_args=["test"])
