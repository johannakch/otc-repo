from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^show_depts/$', views.show_depts, name='show_depts'),
    url(r'^show-event/(?P<id>\d+)/$', views.show_event, name='show_event'),
    url(r'^add-event/(?P<year>[1-9][0-9]{3})/(?P<month>[1-9]|1[0-2])/(?P<day>[1-9]|[1-2][0-9]|3[0-1])/(?P<hour>[8-9]|1[0-9]|2[0-3])$', views.add_event, name='add_event'),
    url(r'', views.index, name='index'),
]
