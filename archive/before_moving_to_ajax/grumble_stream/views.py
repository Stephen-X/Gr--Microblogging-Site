"""
View controller for the global stream page.

Author: Stephen Xie <[redacted]@cmu.edu>
Version: 1.0.0
"""
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse

from webapps.forms import MessageForm
from site_models.models import Message


@login_required
@transaction.atomic  # for message posting
def home_view(request):
    if 'signout' in request.POST:
        # user clicked the sign out button: log out user and return to the login page
        logout(request)
        return redirect(reverse('login'))

    context = {'is_global_view': True}
    current_user = request.user  # the user object of the current user

    # errors: a list for error messages
    errors = []
    context['errors'] = errors

    # total number of grumbles of this user
    context['total_grumbles'] = len(Message.objects.filter(user=current_user))
    # total number of followers the current user has
    context['total_followers'] = len(current_user.followed_by.all())
    # get 20 most recent messages from the database
    # TODO: implement a paging mechanism
    context['messages'] = Message.get_all_ranged(20)

    # just display the page if this is a GET request
    if request.method == 'GET':
        context['message_form'] = MessageForm(auto_id=False)
        return render(request, 'grumblr_stream/grumble_stream.html', context)

    # user would like to post a new message
    if 'message' in request.POST:
        message_form = MessageForm(request.POST, auto_id=False)

        # add error messages from form to the error message list
        # Note: You can access errors without having to call is_valid() first. The form’s data
        # will be validated the first time either you call is_valid() or access errors. However,
        # The validation routines will only get called once, regardless of how many times you access
        # errors or call is_valid(). This means that in order to retrieve error messages,
        # errors must be accessed before is_valid(), otherwise errors will be null (I wonder if this
        # is actually a bug of Django).
        for message in message_form.errors.values():
            # form.errors is a dictionary like this:
            # {'message': ['Message is too long.'], '__all__': ['An error message from clean().']}
            errors.append(message[0])

        if message_form.is_valid():
            # user input is valid: save new message to databasee
            msg_form_instance = message_form.save(commit=False)
            msg_form_instance.user = current_user
            msg_form_instance.save()
            # create new form for another input
            context['message_form'] = MessageForm(auto_id=False)
            # refresh the total grumbles counter
            context['total_grumbles'] += 1
        else:
            # if message is not valid, don't create a new form; preserve the old user input
            context['message_form'] = message_form

    return render(request, 'grumblr_stream/grumble_stream.html', context)


@login_required
@transaction.atomic  # for message posting
def following_view(request):
    if 'signout' in request.POST:
        # user clicked the sign out button: log out user and return to the login page
        logout(request)
        return redirect(reverse('login'))

    context = {'is_following_view': True}
    current_user = request.user  # the user object of the current user

    # errors: a list for error messages
    errors = []
    context['errors'] = errors

    # total number of grumbles of this user
    context['total_grumbles'] = len(Message.objects.filter(user=current_user))
    # total number of followers the current user has
    context['total_followers'] = len(current_user.followed_by.all())
    # get 20 most recent messages from the users the current user is following
    # TODO: implement a paging mechanism
    context['messages'] = Message.get_followers_ranged(current_user, 20)

    # just display the page if this is a GET request
    if request.method == 'GET':
        context['message_form'] = MessageForm(auto_id=False)
        return render(request, 'grumblr_stream/grumble_stream.html', context)

    # user would like to post a new message
    if 'message' in request.POST:
        message_form = MessageForm(request.POST, auto_id=False)

        # add error messages from form to the error message list
        # Note: You can access errors without having to call is_valid() first. The form’s data
        # will be validated the first time either you call is_valid() or access errors. However,
        # The validation routines will only get called once, regardless of how many times you access
        # errors or call is_valid(). This means that in order to retrieve error messages,
        # errors must be accessed before is_valid(), otherwise errors will be null (I wonder if this
        # is actually a bug of Django).
        for message in message_form.errors.values():
            # form.errors is a dictionary like this:
            # {'message': ['Message is too long.'], '__all__': ['An error message from clean().']}
            errors.append(message[0])

        if message_form.is_valid():
            # user input is valid: save new message to databasee
            msg_form_instance = message_form.save(commit=False)
            msg_form_instance.user = current_user
            msg_form_instance.save()
            # create new form for another input
            context['message_form'] = MessageForm(auto_id=False)
            # refresh the total grumbles counter
            context['total_grumbles'] += 1
        else:
            # if message is not valid, don't create a new form; preserve the old user input
            context['message_form'] = message_form

    return render(request, 'grumblr_stream/grumble_stream.html', context)
