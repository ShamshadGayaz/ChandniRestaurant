import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def json_decode(value):
    """Parse JSON string to Python object"""
    try:
        return json.loads(value)
    except:
        return []