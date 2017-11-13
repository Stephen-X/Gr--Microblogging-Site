"""
View controller for the global stream / following page.

Author: Stephen Xie <[redacted]@cmu.edu>
Version: 1.3.0
"""
import logging

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from global_resources.forms import MessageForm
from global_resources.models import Message


# used for printing debugging info in console
logger = logging.getLogger(__name__)


@login_required
@transaction.atomic  # for message posting
@ensure_csrf_cookie
# force the view to set the CSRF token, as the template doesn't explicitly contain the csrf_token tag (it's handled
# in grumbles_control.js)
def home_view(request):
    """
    Note: message display and posting are handled by grumbles_control.js.

    :param request:
    :return:
    """
    context = {'is_global_view': True}
    current_user = request.user  # the user object of the current user

    # errors: a list for error messages
    errors = []
    context['errors'] = errors

    # total number of grumbles of this user
    context['total_grumbles'] = len(Message.objects.filter(user=current_user))
    # total number of followers the current user has
    context['total_followers'] = len(current_user.followed_by.all())

    # just display the page if this is a GET request
    if request.method == 'GET':
        context['message_form'] = MessageForm(auto_id=False)
        return render(request, 'grumblr_stream/grumble_stream.html', context)

    return render(request, 'grumblr_stream/grumble_stream.html', context)


@login_required
@transaction.atomic
@ensure_csrf_cookie
def following_view(request):
    """
    Note: message display is handled by grumbles_control.js.

    :param request:
    :return:
    """
    context = {'is_following_view': True}
    current_user = request.user  # the user object of the current user

    # errors: a list for error messages
    errors = []
    context['errors'] = errors

    # total number of grumbles of this user
    context['total_grumbles'] = len(Message.objects.filter(user=current_user))
    # total number of followers the current user has
    context['total_followers'] = len(current_user.followed_by.all())

    return render(request, 'grumblr_stream/grumble_stream.html', context)
