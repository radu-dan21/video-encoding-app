from crispy_forms.bootstrap import UneditableField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout
from django import forms

from video_coding.entities.models import BaseModel


class BaseReadonlyForm(forms.ModelForm):
    """
    Base class used for read-only forms
    """

    properties: list[str] = []
    field_label_mapping: dict[str, str] = dict()

    def __init__(self, *args, **kwargs):
        self.instance: BaseModel | None = kwargs.get("instance")
        if self.instance:
            kwargs["initial"] = {p: getattr(self.instance, p) for p in self.properties}

        super().__init__(*args, **kwargs)

        self.extra_fields: list[str] = []

        for f in self.properties + self.Meta.fields:
            self.fields[f].disabled = True

        for field_name, label in self.field_label_mapping.items():
            self.fields[field_name].label = label

    @classmethod
    def get_all_fields(cls) -> list[str]:
        return cls.Meta.fields + cls.properties


class RowFormsetHelper(FormHelper):
    form_type: type[BaseReadonlyForm]

    def __init__(self, *args, **kwargs):
        extra_fields: list[str] = (
            kwargs.pop("extra_fields") if "extra_fields" in kwargs else []
        )

        super().__init__(*args, **kwargs)

        self.form_class = "row flex-nowrap overflow-auto"
        fields: list[str] = self.form_type.get_all_fields() + extra_fields
        self.layout = Layout(
            Column(*[UneditableField(f) for f in fields], style="min-width: 300px;"),
        )
