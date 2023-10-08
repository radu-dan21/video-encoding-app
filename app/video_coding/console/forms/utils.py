from django import forms
from django.utils.safestring import mark_safe

from video_coding.entities.models import BaseModel


class ModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, model: type[BaseModel], **kwargs):
        super().__init__(
            queryset=model.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            **kwargs,
        )


def get_bold(s: str) -> str:
    return mark_safe(f"<strong>{s}</strong>")
