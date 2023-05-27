import pprint

from django import template


register = template.Library()


@register.filter
def pretty_json(value):
    return pprint.pformat(value)
