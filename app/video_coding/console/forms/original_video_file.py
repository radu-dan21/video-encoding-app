from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from video_coding.console.forms.base import BaseReadonlyForm
from video_coding.console.forms.utils import ModelMultipleChoiceField
from video_coding.console.layout import get_row
from video_coding.entities.models import (
    VALID_VIDEO_FILE_EXTENSION_LIST,
    VIDEO_FILE_NAME_REGEX,
    ComparisonFilter,
    InformationFilter,
    OriginalVideoFile,
    VideoEncoding,
)
from video_coding.workflows import PrepareMainWorkflow


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

        self.fields["status"].widget = forms.HiddenInput()

        self.helper = FormHelper()
        self.helper.layout = Layout(
            get_row("name", "file_name", "codec"),
            get_row("size", "resolution", "duration", "fps", "bitrate"),
            Field("status"),
        )


class OriginalVideoFileCreateForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=True,
    )
    path = forms.FilePathField(
        path=settings.VIDEOS_FOR_PROCESSING_PATH,
        match=VIDEO_FILE_NAME_REGEX,
        required=False,
    )
    file = forms.FileField(
        required=False,
        validators=[
            FileExtensionValidator(VALID_VIDEO_FILE_EXTENSION_LIST),
        ],
    )
    video_encodings = ModelMultipleChoiceField(
        model=VideoEncoding,
        required=True,
        error_messages={"required": "At least 1 video encoding must be selected!"},
    )
    info_filters = ModelMultipleChoiceField(
        model=InformationFilter,
        required=False,
    )
    comparison_filters = ModelMultipleChoiceField(
        model=ComparisonFilter,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        helper = FormHelper()
        helper.form_method = "post"
        helper.form_class = "form-horizontal"
        helper.label_class = "col-lg-2"
        helper.field_class = "col-lg-8"
        helper.layout = Layout(
            "name",
            "path",
            "file",
            "video_encodings",
            "info_filters",
            "comparison_filters",
        )
        helper.add_input(Submit("submit", "Submit", css_class="btn-primary"))
        self.helper = helper

    def clean_name(self) -> str:
        data = self.cleaned_data["name"]
        if OriginalVideoFile.objects.filter(name=data).exists():
            raise ValidationError("Video with the same name already exists!")
        return data

    def clean(self) -> dict[str, Any]:
        cd: dict[str, Any] = super().clean()
        if not bool(cd["path"]) ^ bool(cd["file"]):
            raise ValidationError(
                "You must either upload a file or select one from the list!"
            )
        return cd

    def save(self) -> tuple[OriginalVideoFile, str]:
        cd: dict[str, Any] = self.cleaned_data

        file_name: str = cd["file"].name if cd["file"] else cd["path"].split("/")[-1]

        ovf = OriginalVideoFile.objects.create(name=cd["name"], file_name=file_name)

        PrepareMainWorkflow(
            ovf_id=ovf.id,
            encoding_ids=cd["video_encodings"].values_list("id", flat=True),
            info_filter_ids=cd["info_filters"].values_list("id", flat=True),
            comparison_filter_ids=cd["comparison_filters"].values_list("id", flat=True),
        ).run()

        return ovf, cd["path"]
