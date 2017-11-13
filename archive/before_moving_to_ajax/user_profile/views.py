"""
View controller for the profile page.

Author: Stephen Xie <[redacted]@cmu.edu>
Version: 1.0.0
"""
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse

from webapps.forms import UserPasswordForm, UserInfoForm, UserExtInfoForm
from site_models.models import Message


@login_required
def profile_view(request):
    if 'signout' in request.POST:
        # user clicked the sign out button: log out user and return to the login page
        logout(request)
        return redirect(reverse('login'))

    context = {}

    # errors: a list for error messages
    errors = []
    context['errors'] = errors

    # --- the following sets up variables that render the page -----------------------------

    # get user to whom the profile page belongs
    user = request.user  # by default the profile page will display info of current user
    url_split = request.path_info.split('/')
    # after split, we should have something like: ['', 'profile', 'username', ''] if user
    # tries to access another user's profile page through "/profile/username/"
    if len(url_split) >= 3 and url_split[2]:  # be mindful of "/profile/"
        # the current user would like to access a different profile
        try:
            user = User.objects.get(username=url_split[2])  # the user object of the current user
            # Note: this will not have an SQL injection vulnerability, as Django will automatically
            # escape SQL queries.
        except User.DoesNotExist:
            # just display the current user profile with a modal warning
            # TODO: create a default "empty" profile page
            errors.append('The user profile you\'re trying to access does not exist.')

    # 'user' is the user of the current profile page; use 'request.user'
    # if you want to access the current user object in template (aka 'view' in MVC)
    context['user'] = user

    # if the current user is viewing other user's profile page, check if he / she is following
    # this other user
    if user != request.user:
        context['is_following'] = user in request.user.ext.following.all()

    # total number of grumbles of this user
    context['total_grumbles'] = len(Message.objects.filter(user=user))
    # total number of followers this user has
    context['total_followers'] = len(user.followed_by.all())
    # get 20 most recent messages posted by this user, ordered by date in descending order (most recent first)
    # TODO: implement a paging mechanism
    context['messages'] = Message.get_ranged(user, 20)

    # form for changing user password
    context['pw_form'] = UserPasswordForm(auto_id=False)

    # forms for changing user profile
    context['profile_form'] = UserInfoForm(auto_id=False)
    # gender choice has an initial value of the user's original setting
    context['profile_ext_form'] = UserExtInfoForm(auto_id=False, initial={'gender': user.ext.gender})

    # --- the following will be invoked if user sends in POST request ----------

    if 'password' in request.POST:
        if __change_password(request, errors):
            errors.append('You successfully changed your password!')
            # TODO: right now for simplicity, success / error messages display all share the same
            # error modal; the main form modal closes whenever a page is refreshed / re-rendered,
            # therefore it seems impossible to display feedback inside the forms.
            # TODO: The proper way to do this will be to utilize Django's messages framework to provide
            # one time feedback after successful submission, and apply the PRG design pattern.
            # See comments below for details on PRG.

    if 'user_info_mod' in request.POST:
        if __modify_profile(request, errors):
            """
            For weird reasons (probably a bug in Django), when the User object is updated (we modify
            the first_name, last_name and email fields in __modify_profile) and the page is re-rendered,
            first_name and last_name values are not updated instantly in the template. User will need to
            manually refresh the page again for the visual changes (i.e. user's name on the profile cover) to
            take effect. However, refreshing the page by clicking the refresh button will cause the previous
            POST to be resubmitted again. Therefore I followed the PRG (Post/Redirect/Get) design pattern
            and used redirect here to prevent resubmission while invoking a page reload.
            
            Because we must use Django's messages framework to pass success feedback under PRG pattern, for now
            I'll just reload the page without the success notification (since it's not the main priority for this
            assignment).
            """
            # Note: for email changes the function will not return true, but rather a prompt
            # of checking confirmation email.
            return redirect(reverse('profile'))

    if 'follow' in request.POST:
        request.user.ext.following.add(user)
        return redirect(request.path_info)

    if 'unfollow' in request.POST:
        request.user.ext.following.remove(user)
        return redirect(request.path_info)

    return render(request, 'grumblr_profile/profile.html', context)


@login_required
@transaction.atomic
def __change_password(request, errors):
    """
    Allow user to change password if they pass the
    password confirmation test.

    :param request: the request object from the template
    :param errors: the list used to collect error messages
    :return: a boolean value indicating if password changing has completed
    """
    form = UserPasswordForm(request.POST)
    current_user = request.user

    # add error messages from form to the error message list if there're any
    # the form will be evaluated when form.errors is called
    for message in form.errors.values():
        # form.errors is a dictionary like this:
        # {'email': ['Enter a valid email address.'], '__all__': ['Passwords did not match.']}
        errors.append(message[0])

    if form.is_valid():
        new_pass = form.cleaned_data['password']
        current_user = User.objects.get(username__exact=current_user)
        current_user.set_password(new_pass)
        current_user.save()

        # log user in using the new credential
        current_user = authenticate(request, username=current_user.username, password=new_pass)
        if current_user is not None:
            login(request, current_user)
        else:
            errors.append('Something\'s wrong when trying to log you in with the new password;'
                          ' you may need to do it manually.')

        return True

    return False


@login_required
@transaction.atomic
def __modify_profile(request, errors):
    """
    Allow users to change their own profile information.

    :param request:
    :param errors:
    :return: except email
    """
    current_user = request.user
    form = UserInfoForm(request.POST)
    # files passed in through request will be available in request.FILES dictionary
    form_ext = UserExtInfoForm(request.POST, request.FILES)

    for message in form.errors.values():
        errors.append(message[0])
    for message in form_ext.errors.values():
        errors.append(message[0])

    if form.is_valid() and form_ext.is_valid():
        user = User.objects.get(username__exact=current_user)
        user_ext = user.ext

        # only modify corresponding entry in database when the field is not empty
        if 'avatar' in form_ext.cleaned_data and form_ext.cleaned_data['avatar']:
            user_ext.avatar = form_ext.cleaned_data['avatar']
        if 'first_name' in form.cleaned_data and form.cleaned_data['first_name']:
            user.first_name = form.cleaned_data['first_name']
        if 'last_name' in form.cleaned_data and form.cleaned_data['last_name']:
            user.last_name = form.cleaned_data['last_name']
        if 'email' in form.cleaned_data and form.cleaned_data['email']:
            # TODO: send confirmation email before modifying
            user.email = form.cleaned_data['email']
        if 'signature' in form_ext.cleaned_data and form_ext.cleaned_data['signature']:
            user_ext.signature = form_ext.cleaned_data['signature']
        if 'gender' in form_ext.cleaned_data and form_ext.cleaned_data['gender']:
            user_ext.gender = form_ext.cleaned_data['gender']
        if 'age' in form_ext.cleaned_data and form_ext.cleaned_data['age']:
            user_ext.age = form_ext.cleaned_data['age']
        if 'hometown' in form_ext.cleaned_data and form_ext.cleaned_data['hometown']:
            user_ext.hometown = form_ext.cleaned_data['hometown']
        if 'hobby' in form_ext.cleaned_data and form_ext.cleaned_data['hobby']:
            user_ext.hobby = form_ext.cleaned_data['hobby']
        if 'bio' in form_ext.cleaned_data and form_ext.cleaned_data['bio']:
            user_ext.bio = form_ext.cleaned_data['bio']

        user.save()
        user_ext.save()
        return True

    return False
