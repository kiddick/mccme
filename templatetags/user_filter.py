from django import template

register = template.Library()

def _get(value, arg):
    if arg == 'uid':
        return value.pid

register.filter('_get', _get)
