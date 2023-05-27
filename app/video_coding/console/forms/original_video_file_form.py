from django.forms import ModelForm

from video_coding.entities.models import OriginalVideoFile


class OriginalVideoFileForm(ModelForm):
    class Meta:
        model = OriginalVideoFile
        fields = [
            "name",
            "file_name",
            "status",
            "error_message",
            "ffprobe_info",
        ]
