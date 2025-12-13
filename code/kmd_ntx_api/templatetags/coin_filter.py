import json
from django import template
from kmd_ntx_api.cache_data import JsonSerde
register = template.Library()

@register.filter(name='cut')
def cut(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, '')

@register.filter
def clean_underscore(value):
    """Removes all values of arg from the given string"""
    return value.replace("_", ' ')

@register.filter
def pretty_json(value):
    return json.dumps(value, indent=4, default=JsonSerde._json_default)

@register.filter
def json_str(value):
    return json.dumps(value, default=JsonSerde._json_default)
