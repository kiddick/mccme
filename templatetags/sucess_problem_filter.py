from django import template

register = template.Library()

def _get(value, arg):
    if arg == 'uid':
        return value.uid
    elif arg == 'plabel':
        return value.plabel
    elif arg == 'timestamp':
        return value.timestamp

register.filter('_get', _get)
