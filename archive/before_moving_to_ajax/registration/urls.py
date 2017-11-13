from django.conf.urls import url

from . import views

# Note that "name" attribute is used by the "url" template tag for linking to the registration page
# in the login app
urlpatterns = [
    url(r'^$', views.register_view, name='register'),
    url(r'^reset', views.reset_view, name='reset')
]
