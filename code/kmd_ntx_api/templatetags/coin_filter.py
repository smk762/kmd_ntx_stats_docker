import json
from django import template
register = template.Library()

@register.filter(name='cut')
def cut(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, '')

@register.filter
def pretty_json(value):
    return json.dumps(value, indent=4)

@register.filter
def json_str(value):
    return json.dumps(value)
