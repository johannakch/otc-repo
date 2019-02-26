from django.conf.urls import url, include
from django.contrib.auth import views

urlpatterns = [
    url('login/', views.login, name='login'),
    url('logout/', views.logout, name='logout'),
    url('^password-change/done/$', views.password_change_done,
        {'template_name': 'registration/password_change_done.html'}, name='password_change_done'),
    url('^password-change/$', views.password_change,
        {'template_name': 'registration/password_change_form.html', 'post_change_redirect': 'password_change_done'}, name='password_change'),


]