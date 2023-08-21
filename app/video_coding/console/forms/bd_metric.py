from django import forms

from video_coding.console.forms.base import BaseReadonlyForm, RowFormsetHelper
from video_coding.entities.models import BDMetric


class BDMetricReadonlyForm(BaseReadonlyForm):
    class Meta:
        model = BDMetric
        fields = [
            "reference_codec",
            "test_codec",
            "video_filter",
            "bd_rate",
            "bd_metric",
        ]


BDMetricFormset = forms.modelformset_factory(
    BDMetric,
    form=BDMetricReadonlyForm,
    extra=0,
)


class BDMetricFormsetHelper(RowFormsetHelper):
    form_type = BDMetricReadonlyForm
