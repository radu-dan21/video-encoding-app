from django import forms

from video_coding.entities.models import BaseModel


class ModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, model: type[BaseModel], **kwargs):
        super().__init__(
            queryset=model.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            **kwargs,
        )
