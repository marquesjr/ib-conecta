from django import template

register = template.Library()


@register.filter
def person_name(user) -> str:
    """Nome completo da pessoa; o login aparece só quando o cadastro não tem nome."""
    if user is None:
        return ""
    return user.get_full_name() or user.username
