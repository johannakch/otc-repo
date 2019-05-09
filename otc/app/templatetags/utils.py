from django import template
from django.contrib.auth.models import User
from django.forms.boundfield import BoundWidget

from ..utils import get_year_dic

register = template.Library()

@register.filter
def format_month(month):
    dic = get_year_dic()
    return dic[month]

@register.filter
def get_item(dic, key):
    return dic[key]

@register.filter
def is_not_self(item, current_user):
    if item.data['label'] != current_user and item.data['label'] != 'anonym':
        return True
    return False

@register.filter
def format_name(item):
    full_name = User.objects.filter(username=item.data['label'])[0].get_full_name()
    item.data.update({
        'label': full_name
    })
    new = BoundWidget(item.parent_widget, item.data, item.renderer)
    return new
