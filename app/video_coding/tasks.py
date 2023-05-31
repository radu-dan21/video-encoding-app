import logging
import shutil

from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task(queue="web")
def run_ovf_workflow(ovf_id: int, *args, **kwargs):
    # avoiding circular import
    from video_coding.entities.models import OriginalVideoFile

    OriginalVideoFile.objects.get(id=ovf_id).run_workflow()


@shared_task(queue="web")
def remove_file_tree(path: str, *args, **kwargs):
    shutil.rmtree(path, ignore_errors=True)
