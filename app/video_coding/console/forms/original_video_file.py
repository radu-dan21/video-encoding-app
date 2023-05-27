from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

from video_coding.entities.models import OriginalVideoFile
from video_coding.console.layout import get_row


class OriginalVideoFileForm(forms.ModelForm):
    size = forms.CharField()
    codec = forms.CharField()
    resolution = forms.CharField()
    fps = forms.FloatField()
    bitrate = forms.FloatField()
    duration = forms.FloatField()

    class Meta:
        model = OriginalVideoFile
        fields = [
            "name",
            "file_name",
            "status",
            "error_message",
        ]

    properties: list[str] = [
        "bitrate",
        "duration",
        "size",
        "codec",
        "fps",
        "resolution",
    ]

    def __init__(self, *args, **kwargs):
        instance: OriginalVideoFile | None = kwargs.get("instance")
        if instance:
            kwargs["initial"] = {p: getattr(instance, p) for p in self.properties}

        super().__init__(*args, **kwargs)

        for f in self.properties + self.Meta.fields:
            self.fields[f].disabled = True

        self.fields['bitrate'].label = 'Bitrate (Mbps)'
        self.fields['duration'].label = 'Duration (seconds)'

        self.helper = FormHelper()
        self.helper.layout = Layout(
                get_row('name', 'file_name', 'codec'),
                get_row('size', 'resolution', 'duration', "fps"),
        )
