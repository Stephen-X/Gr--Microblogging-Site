"""
Backend APIs.

Author: Stephen Xie <[redacted]@cmu.edu>
Version: 1.1.0
"""
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone

from .forms import CommentForm, MessageForm
from .models import Comment, Message


# used for printing debugging info in console
logger = logging.getLogger(__name__)


@login_required
@transaction.atomic  # for message posting
def post_message(request):
    """
    API used by frontend JS to post a grumble (message).
    :param request:
    :return:
    """
    if 'message' not in request.POST or not request.POST['message']:
        raise Http404
    else:
        current_user = request.user  # the user object of the current user

        message_form = MessageForm(request.POST, auto_id=False)

        if message_form.is_valid():
            # user input is valid and not empty / null: save new message to databasee
            msg_form_instance = message_form.save(commit=False)
            msg_form_instance.user = current_user
            msg_form_instance.save()
        else:
            return HttpResponseBadRequest('Invalid message data.')

    return HttpResponse('')  # empty response on success


@login_required
def get_messages(request, view='global', from_t='1970-01-01T00:00+00:00'):
    """
    API used to get a list of latest messages since the given time frame.
    Note: this method is only for global and following views; for profile
    view see get_profile_messages.

    :param request:
    :param view: either 'global' view or 'follower' view
    :param from_t: the starting time (excluded)
    :return: a JSON string
    """
    view_name = view.lower()
    user = request.user  # get current user

    context = {}

    if view_name == 'global':
        # get 20 most recent messages from the database
        # TODO: implement a paging mechanism
        context['messages'] = Message.get_all_ranged(from_date=from_t)

    elif view_name == 'follower':
        # get 20 latest messages that are posted later than from_t from the followed users
        # TODO: implement a paging mechanism
        context['messages'] = Message.get_followers_ranged(user, from_date=from_t)

    else:
        raise Http404

    context['last_updated'] = timezone.now().isoformat()  # last updated time string in ISO 8601 format

    return render(request, 'messages_template.json', context, content_type='application/json')


@login_required
def get_profile_messages(request, profile_user, from_t='1970-01-01T00:00+00:00'):
    """
    API used to get a list of latest messages since the given time frame.
    Note: this method is only for profile view; for global and following
    views see get_messages.

    :param request:
    :param profile_user: ID of the user to which the profile belongs
    :param from_t: the starting time (excluded)
    :return: a JSON string
    """
    context = {}

    try:
        user = User.objects.get(username=profile_user)
        # Note: this will not have an SQL injection vulnerability, as Django will automatically
        # escape SQL queries.
    except User.DoesNotExist:
        raise Http404

    # get 20 most recent messages posted by this user, ordered by date in descending order (most recent first)
    # TODO: implement a paging mechanism
    context['messages'] = Message.get_user_ranged(user, from_date=from_t)

    context['last_updated'] = timezone.now().isoformat()  # last updated time string in ISO 8601 format

    return render(request, 'messages_template.json', context, content_type='application/json')


@login_required
@transaction.atomic
def post_comment(request, msg_id):
    """
    API used to post a comment to a specified message.
    :param request:
    :param msg_id: ID of the message this comment belongs to
    :return:
    """
    if 'content' not in request.POST or not request.POST['content']:
        raise Http404
    else:
        current_user = request.user  # the user object of the current user
        try:  # get the message from database
            message = Message.objects.get(id=msg_id)
        except:
            raise Http404

        comment_form = CommentForm(request.POST, auto_id=False)

        if comment_form.is_valid():
            # user input is valid and not empty / null: save new message to databasee
            comm_form_instance = comment_form.save(commit=False)
            comm_form_instance.from_user = current_user
            comm_form_instance.message = message
            comm_form_instance.save()
        else:
            return HttpResponseBadRequest('Invalid comment data.')

    return HttpResponse('')  # empty response on success


@login_required
def get_comments(request, msg_id, from_t='1970-01-01T00:00+00:00'):
    """
    API used to retrieve all latest comments made to a specified message
    since the given start time.

    :param request:
    :param msg_id: ID of the message this comment belongs to
    :param from_t: the starting time (excluded)
    :return: a JSON string
    """
    context = {'message_id': msg_id}
    try:
        message = Message.objects.get(id=msg_id)
        # get the latest 20 comments that are posted later than from_t
        # TODO: implement a paging mechanism
        context['comments'] = Comment.get_all_ranged(message, from_date=from_t)

    except:
        raise Http404

    context['last_updated'] = timezone.now().isoformat()  # last updated time string in ISO 8601 format

    return render(request, 'comments_template.json', context, content_type='application/json')
