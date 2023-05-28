from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms

from video_coding.console.forms.base import BaseReadonlyForm
from video_coding.console.layout import get_row
from video_coding.entities.models import OriginalVideoFile


class OriginalVideoFileDetailsReadonlyForm(BaseReadonlyForm):
    class Meta:
        model = OriginalVideoFile
        fields = [
            "name",
            "file_name",
            "status",
            "error_message",
        ]

    properties: list[str] = [
        "codec",
        "size",
        "resolution",
        "duration",
        "fps",
        "bitrate",
    ]

    codec = forms.CharField()
    size = forms.CharField()
    resolution = forms.CharField()
    duration = forms.FloatField()
    fps = forms.FloatField()
    bitrate = forms.FloatField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            get_row("name", "file_name", "codec"),
            get_row("size", "resolution", "duration", "fps", "bitrate"),
        )
