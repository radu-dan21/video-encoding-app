from crispy_forms.layout import Div, Column


class Row(Div):
    css_class = "form-row"


def get_row(*field_names: list[str]):
    return Row(*[Column(f) for f in field_names])
