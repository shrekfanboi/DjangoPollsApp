from django import template
from datetime import datetime
from django.utils.timesince import timesince
import pytz

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    class_attr = field.field.widget.attrs.get('class', '')
    return field.as_widget(attrs={"class": class_attr + ' ' + css_class})

@register.filter(name='add_event_handler')
def add_event_handler(field, event, handler):
    return field.as_widget(attrs={event: handler})

@register.filter(name='timesince_approx')
def timesince_approx(value):
    if not value:
        return ""
    
    now = datetime.now(pytz.utc) if value.tzinfo else datetime.now()
    value = value.astimezone(pytz.utc) if value.tzinfo else value    
    time_since = timesince(value, now)

    units = time_since.split(", ")
    if units:
        return units[0]  # Get the largest unit

    return time_since
