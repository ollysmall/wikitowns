from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def upto(value, delimiter=None):
    return value.split(delimiter)[0]
upto.is_safe = True


# used to get the class name of models
@register.filter
def classname(obj):
    return obj.__class__.__name__
