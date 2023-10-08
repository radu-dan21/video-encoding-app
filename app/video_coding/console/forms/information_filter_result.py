from django import forms

from video_coding.console.forms.base import BaseReadonlyForm, RowFormsetHelper
from video_coding.entities.models import InformationFilterResult


class InformationFilterResultReadonlyForm(BaseReadonlyForm):
    class Meta:
        model = InformationFilterResult
        fields = [
            "information_filter",
            "compute_time",
            "output",
        ]

    field_label_mapping = {"compute_time": "Compute time (seconds)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        output: str = kwargs["instance"].output
        description: str = kwargs["instance"].information_filter.description

        self._create_output_field(
            field_type=forms.CharField,
            name="description",
            output=description,
        )

        textarea_field_value_map: dict[str, str] = {
            "description": description,
            "output": output,
        }
        for field_name, field_value in textarea_field_value_map.items():
            self.fields[field_name].widget = forms.Textarea(
                attrs={"rows": field_value.count("\n") + 1}
            )


InformationFilterResultFormset = forms.modelformset_factory(
    InformationFilterResult,
    form=InformationFilterResultReadonlyForm,
    extra=0,
)


class InformationFilterResultFormsetHelper(RowFormsetHelper):
    form_type = InformationFilterResultReadonlyForm
