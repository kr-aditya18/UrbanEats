from django import template

register = template.Library()

@register.filter
def filter_day(opening_hours_qs, day_value):
    """
    Filters a queryset/list of OpeningHour objects by day value.
    Usage in template:  {{ opening_hours|filter_day:day_value }}
    """
    return [oh for oh in opening_hours_qs if oh.day == day_value]