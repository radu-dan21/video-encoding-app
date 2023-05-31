from django import forms

from video_coding.console.forms.base import BaseReadonlyForm, RowFormsetHelper
from video_coding.entities.models import InformationFilterResult


class InformationFilterResultReadonlyForm(BaseReadonlyForm):
    class Meta:
        model = InformationFilterResult
        fields = [
            "video_filter",
            "compute_time",
            "output",
        ]

    field_label_mapping = {"compute_time": "Compute time (seconds)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["output"].widget = forms.Textarea(attrs={"rows": 13})


InformationFilterResultFormset = forms.modelformset_factory(
    InformationFilterResult,
    form=InformationFilterResultReadonlyForm,
    extra=0,
)


class InformationFilterResultFormsetHelper(RowFormsetHelper):
    form_type = InformationFilterResultReadonlyForm
