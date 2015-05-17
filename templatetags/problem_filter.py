from django import template

register = template.Library()

def _get(value, arg):
    if arg == 'pid':
        return value.pid
    elif arg == 'submits':
        return value.submits

register.filter('_get', _get)
