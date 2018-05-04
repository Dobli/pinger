from django import template

register = template.Library()


@register.simple_tag
def is_active(request, pattern):
    """Check url to decide if navigation is active.

    :request: http request of page
    :pattern: the pattern to check against
    :returns: the class of an active mdl element

    """
    import re
    pattern = "^%s$" % pattern
    if re.search(pattern, request.path):
        return 'is-active'
    return ''
