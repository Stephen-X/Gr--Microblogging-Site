from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^post-message/', views.post_message),

    url(r'^get-messages/$', views.get_messages, name='get-messages'),
    url(r'^get-messages/profile/(?P<profile_user>[^/]+?)/$', views.get_profile_messages),
    url(r'^get-messages/profile/(?P<profile_user>[^/]+?)/(?P<from_t>[^/]+?)/$', views.get_profile_messages),
    url(r'^get-messages/(?P<view>\w+)/$', views.get_messages),  # (?P<py_func_parameter>pattern) is a Python regex group
    url(r'^get-messages/(?P<view>\w+)/(?P<from_t>[^/]+?)/$', views.get_messages),

    url(r'^post-comment/(?P<msg_id>[^/]+?)/$', views.post_comment),

    url(r'^get-comments/(?P<msg_id>[^/]+?)/$', views.get_comments),
    url(r'^get-comments/(?P<msg_id>[^/]+?)/(?P<from_t>[^/]+?)/$', views.get_comments)
]
