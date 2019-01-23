from django.conf.urls import url, include
from django.contrib.auth.views import login, logout

urlpatterns = [
    url(r'', login, {'template_name': 'registration/login.html'}),
    url(r'logout', logout, name='logout'),
]