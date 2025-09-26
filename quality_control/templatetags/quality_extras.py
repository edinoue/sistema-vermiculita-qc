from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Filtro para acessar um dicionário por chave no template"""
    return dictionary.get(key)
