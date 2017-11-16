"""
View controller for the registration page.

Author: Stephen Xie <[redacted]@cmu.edu>
Version: 1.1.0
"""
import logging

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse

from global_resources.forms import UserRegisterForm
from global_resources.models import UserExtended


# used for printing debugging info in console
logger = logging.getLogger(__name__)


@transaction.atomic
def register_view(request):
    """
    Controller of the register view.

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
            form = UserRegisterForm(auto_id=False)
            context['form'] = form
            return render(request, 'grumblr_register/registration.html', context)

    # errors: a list for error messages
    errors = []
    context['errors'] = errors

    # *** user must have clicked the sign up button (this is a POST): begin validation ***

    # create a form instance of UserLoginForm and populate it with data
    # from request
    form = UserRegisterForm(request.POST, auto_id=False)

    # add error messages from form to the error message list if there're any
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
        # user input is valid: create new user profile
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']

        new_user = User.objects.create_user(username=username, password=password, email=email,
                                            first_name=first_name, last_name=last_name)
        new_user.is_active = False  # new users are inactive by default
        new_user.save()
        # initialize extended profile information for this user
        new_user_extended = UserExtended(user=new_user)
        new_user_extended.save()

        # send verification email to the user
        __send_confirmation_email(request, new_user, errors)

        # # then log user in and redirect to his/her main page
        # user = authenticate(request, username=username, password=password)
        # login(request, user)
        # # if user was redirected here from other pages by the authentication system, Django includes a "next" value
        # # containing the original URL as a query string to the redirected URL.
        # next_url = request.GET.get('next')
        # if next_url:
        #     return redirect(next_url)  # redirect user to the original page they were trying to access
        # else:
        #     return redirect(reverse('home'))  # or just redirect to the main page

    # send this form to the html view
    context['form'] = form

    return render(request, 'grumblr_register/registration.html', context)


# TODO: temporary use errors modal to notify user
def __send_confirmation_email(request, new_user, errors):
    # generat an email token for this new user
    token = default_token_generator.make_token(new_user)

    email_body = 'Welcome to the grumblr site! Please click the link below to verify your email address and complete ' \
                 'your registration:\nhttp://%s%s%s\n\n\nThe Grumblr Admin team\n'.strip() % (
                     request.get_host(),
                     reverse('user_verify'),
                     "?username=" + new_user.username + "&token=" + token)

    send_mail(subject='Verify your email address',
              message=email_body,
              from_email='admin@grumblr.com',  # for dummy SMTP server
              recipient_list=[new_user.email]
              )

    errors.append('Thank you for registering! Please check your email for confirmation email.')
