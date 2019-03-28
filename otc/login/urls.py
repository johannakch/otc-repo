from django.conf.urls import url
from django.contrib.auth import views

from .views import request_new_password


urlpatterns = [
    url('login/', views.login, name='login'),
    url('logout/', views.logout, name='logout'),
    url('^password-change/done/$', views.password_change_done,
        {'template_name': 'registration/password_change_done.html'}, name='password_change_done'),
    url('^password-change/$', views.password_change,
        {'template_name': 'registration/password_change_form.html', 'post_change_redirect': 'password_change_done'}, name='password_change'),
    url('^request-new-password/$', request_new_password, name='request_new_password'),
]