from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # url(r'^', include('django.contrib.auth.urls')),  # use all the django built-in authentication views
    url(r'^login/$', views.login_view, name='login'),
    url(r'^user_verify/', views.verify_view, name='user_verify'),
    url(r'^password_reset$',
        auth_views.PasswordResetView.as_view(
            template_name='grumblr_auth/password_reset_form.html',
            email_template_name='grumblr_auth/password_reset_email.html'),
        name='password_reset'),
    url(r'^password_reset/done/$',
        auth_views.PasswordResetDoneView.as_view(
            template_name='grumblr_auth/password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='grumblr_auth/password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/done/$',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='grumblr_auth/password_reset_complete.html'),
        name='password_reset_complete'),
    url(r'^logout/$',
        # redirect user to the login page once logout is successful
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout')
]
