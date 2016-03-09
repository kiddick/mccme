from django import template

register = template.Library()

def _get(value, arg):
    if arg == 'uid':
        return value.uid
    if arg == 'uname':
        return value.uname

register.filter('_get', _get)
