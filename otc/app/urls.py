from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^add-event/(?P<year>[1-9][0-9]{3})/(?P<month>[1-9]|1[0-2])/(?P<day>[1-9]|[1-2][0-9]|3[0-1])/$', views.add_event, name='add_event'),
    url(r'', views.index, name='index'),

]