from django.conf.urls import url, include

from . import views

urlpatterns = [
    url('^', include('django.contrib.auth.urls')),
    url(r'^$', views.login_view, name='login'),
    url(r'^verify', views.verify_view, name='verify'),
]
