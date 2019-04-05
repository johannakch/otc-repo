from django import template

from ..utils import get_year_dic

register = template.Library()

@register.filter
def format_month(month):
    dic = get_year_dic()
    return dic[month]

@register.filter
def get_item(dic, key):
    print(dic[key])
    return dic[key]