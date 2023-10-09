from django import forms
from django.utils.safestring import mark_safe

from video_coding.entities.models import BaseModel


class ModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, model: type[BaseModel], all_selected=False, **kwargs):
        all_objects = model.objects.all()
        initial = list(all_objects) if all_selected else []
        super().__init__(
            queryset=model.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            initial=initial,
            **kwargs,
        )


def get_bold(s: str) -> str:
    return mark_safe(f"<strong>{s}</strong>")
