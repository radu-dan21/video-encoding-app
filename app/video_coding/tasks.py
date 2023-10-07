import logging
import os
import shutil

from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task(queue="web", acks_late=True)
def run_ovf_workflow(ovf_id: int, file_path: str, *args, **kwargs):
    """
    Idempotent Celery task used for processing an OriginalVideoFile
    :param ovf_id: OriginalVideoFile id
    :param file_path: Path to the original video
    """
    from video_coding.entities.models import OriginalVideoFile

    ovf = OriginalVideoFile.objects.get(id=ovf_id)
    if file_path and not ovf.ffprobe_info:
        ovf.handle_file_copy(file_path)
    ovf.run_workflow()


@shared_task(queue="web", acks_late=True)
def remove_file_tree(path: str, *args, **kwargs):
    """
    Idempotent Celery task used for deleting files
    Used for cleanup when deleting an OriginalVideoFile
    :param path: Path to the file/directory that should be deleted
    """
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    else:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
