from django import forms

from video_coding.console.forms.base import BaseReadonlyForm, RowFormsetHelper
from video_coding.entities.models import EncodedVideoFile


class EncodedVideoFileReadonlyForm(BaseReadonlyForm):
    class Meta:
        model = EncodedVideoFile
        fields = [
            "video_encoding",
            "encoding_time",
        ]

    properties: list[str] = [
        "bitrate",
        "size",
        "codec",
    ]

    size = forms.CharField()
    codec = forms.CharField()
    bitrate = forms.FloatField()

    field_label_mapping = {
        "bitrate": "Bitrate (kbps)",
        "encoding_time": "Encoding time (seconds)",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for each ComparisonFilterResult,
        # add a new form field that contains the quality score
        for cfr in self.instance.decoded_video_file.cfrs:
            name: str = cfr.video_filter.name
            self.extra_fields.append(name)
            value = cfr.value
            self._create_output_charfield(
                name,
                str(value) if value is not None else "",
            )

    def _create_output_charfield(self, name: str, output: str) -> None:
        self.fields[name] = forms.CharField(label=name)
        self.fields[name].initial = output
        self.fields[name].disabled = True


EncodedVideoFileFormset = forms.modelformset_factory(
    EncodedVideoFile,
    form=EncodedVideoFileReadonlyForm,
    extra=0,
)


class EncodedVideoFileFormsetHelper(RowFormsetHelper):
    form_type = EncodedVideoFileReadonlyForm
