"""
View controller for the login page.

Author: Stephen Xie <[redacted]@cmu.edu>
Version: 1.2.0
"""
import logging
from urllib.parse import parse_qs

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse

from global_resources.forms import UserLoginForm

# used for printing debugging info in console
logger = logging.getLogger(__name__)


def login_view(request):
    """
    Controller of the login view.

    :param request: request object from the front view
    :return: None
    """
    context = {}  # used to pass data to the html view

    # Get the next parameter from the URL query string and pass along (through the Sign Up form in the HTML view);
    # This is used by the Django authentication system to redirect back to the original page once user logs in.
    if request.GET.urlencode():
        context['next_url'] = request.GET.urlencode()

    # just display the page if this is a GET request
    if request.method == 'GET':
        if request.user.is_authenticated:
            # this user has already logged in; redirect to home page
            return redirect(reverse('home'))
        else:
            # generate a blank form for users to fill in
            # when auto_id is set to False, no <label> tags nor id attributes will
            # be appended to the input field in HTML view
            form = UserLoginForm(auto_id=False)
            context['form'] = form
            return render(request, 'grumblr_auth/login.html', context)

    # errors: a list for error messages
    errors = []
    context['errors'] = errors

    # ******* this is a POST, begin validation ********************************

    # create a form instance of UserLoginForm and populate it with data
    # from request
    form = UserLoginForm(request.POST, auto_id=False)

    # append values of the error messages dictionary from form to the error message list
    # Note: You can access errors without having to call is_valid() first. The form’s data
    # will be validated the first time either you call is_valid() or access errors. However,
    # The validation routines will only get called once, regardless of how many times you access
    # errors or call is_valid(). This means that in order to retrieve error messages,
    # errors must be accessed before is_valid(), otherwise errors will be null (I wonder if this
    # is actually a bug of Django).
    for message in form.errors.values():
        # form.errors is a dictionary like this:
        # {'email': ['Enter a valid email address.'], '__all__': ['Passwords did not match.']}
        errors.append(message[0])

    if form.is_valid():
        # user input passed all tests defined in form
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        if 'reset' in request.POST:
            # user wants to reset password
            return redirect(reverse('password_reset'))

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # user data is valid: log user in
            login(request, user)
            # if user was redirected here from other pages by the authentication system, Django includes a "next"
            # value containing the original URL as a query string to the redirected URL.
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)  # redirect user to the original page they were trying to access
            else:
                return redirect(reverse('home'))  # or just redirect to the main page
        else:
            # user data is invalid: report error and create a new blank form
            form = UserLoginForm(auto_id=False)
            errors.append('Your username and password did not match our record.')

    else:
        # user input didn't pass the form validation; reset form
        form = UserLoginForm(auto_id=False)

    # send this form to the html view
    context['form'] = form

    return render(request, 'grumblr_auth/login.html', context)


# this metadata guarantees that writing to user model database is atomic (i.e. either write all or don't write at all)
# Note: avoid catching errors esp. DatabaseError and its subclasses in atomic blocks;
# for more, see here: https://docs.djangoproject.com/en/1.11/topics/db/transactions/
@transaction.atomic
def verify_view(request):
    # TODO: incorporate with login_view; right now this page can only be used for verification
    context = {}

    errors = []
    context['errors'] = errors

    if request.user.is_authenticated:
        # this user has already logged in; redirect to home page
        return redirect(reverse('home'))
    else:
        # get username and token out from the query string
        query_string = request.GET.urlencode()  # something like "username=***&token=***"
        parsed_query = parse_qs(query_string)
        # something like {'username': ['***'], 'token': ['***']}

        try:
            user = User.objects.get(username__exact=parsed_query['username'][0])
            token = parsed_query['token'][0]
        except:
            user = None
            errors.append('Missing valid username or token.')

        if user is not None and default_token_generator.check_token(user, token):
            # user passed test; redirect to login page
            user.is_active = True
            user.save()
            return redirect(reverse('login'))
        elif user is not None:
            errors.append('Verification failed.')

    return render(request, 'grumblr_auth/user_verify.html', context)
