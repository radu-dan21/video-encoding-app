from crispy_forms.layout import Column, Div


class Row(Div):
    css_class = "form-row"


def get_row(*field_names: list[str]) -> Row:
    return Row(*[Column(f) for f in field_names])
