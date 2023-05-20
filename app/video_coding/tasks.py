import logging

from celery import shared_task
from video_coding.entities.models import OriginalVideoFile


logger = logging.getLogger(__name__)


@shared_task(queue="web")
def run_ovf_workflow(ovf_id: int, *args, **kwargs):
    OriginalVideoFile.objects.get(id=ovf_id).run_workflow()
