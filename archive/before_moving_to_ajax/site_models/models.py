"""
Global models for the grumblr site.

Unfortunately we have to create a separate app for global models instead of putting
it in the project directory ("grumblr_site"), as models can only be recognized by
editing the "INSTALLED_APPS" setting.

Remember to run <code>manage.py migrate</code> every time this file is modified.

Author: Stephen Xie <[redacted]@cmu.edu>
Version: 1.1.0
"""
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Message(models.Model):
    """
    The message class.
    """
    # the user who sent this message
    # on_delete=models.CASCADE: similar to the SQL constraint ON DELETE CASCADE,
    #   Django will also delete the object containing the ForeignKey
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # date this message is posted;
    # this will be automatically set to now when the object is first created
    date = models.DateTimeField(auto_now_add=True)
    # message text;
    # limited to 42 characters max
    message = models.CharField(max_length=42)
    # an optional photo to be included in the message
    # photo = models.ImageField(upload_to='user-msg-photos', blank=True)

    @staticmethod
    def get_all_ranged(mrange, offset=0):
        """
        Get a range of messages from all the records in the database,
        sorted in reverse-chronological order. The method is designed for
        pagination in messages display.

        :param mrange: how many messages will be returned
        :param offset: index of the first message in the list (0-based)
        :return: a range of ordered messages
        """
        return Message.objects.order_by('-date')[offset:offset+mrange]

    @staticmethod
    def get_ranged(user, mrange, offset=0):
        """
        Get a range of messages from all the records of the given user,
        sorted in reverse-chronological order. The method is designed for
        pagination in messages display.

        :param user: the given user
        :param mrange: how many messages will be returned
        :param offset: index of the first message in the list (0-based)
        :return: a range of ordered messages
        """
        return Message.objects.filter(user=user).order_by('-date')[offset:offset+mrange]

    @staticmethod
    def get_followers_ranged(user, mrange, offset=0):
        """
        Get a range of messages from all the records of users this current
        user is following, sorted in reverse-chronological order.
        The method is designed for pagination in messages display.

        :param mrange: how many messages will be returned
        :param offset: index of the first message in the list (0-based)
        :return: a range of ordered messages
        """
        # first get all followers
        followers = user.ext.following.all()
        # then search and sort
        return Message.objects.filter(user__in=followers).order_by('-date')[offset:offset+mrange]


def user_avatar_dir(instance, filename):
    """
    Helper functions for determining file upload locations.
    Files will be uploaded to [MEDIA_ROOT]/user_<id>/avatar/<filename>
    :param instance: an instance of the model where the ImageField is defined
    :param filename: the filename that was originally given to the file
    :return: the file path to be uploaded to
    """
    return 'user_{0}/avatar/{1}'.format(instance.user.id, filename)


class UserExtended(models.Model):
    """
    Stores extended properties for the User model. This is not a replacement
    of the default User model.
    For more: https://docs.djangoproject.com/en/1.11/topics/auth/customizing/#extending-the-existing-user-model
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='ext',  # UserExtended fields can now be accessed from the base User object via user.ext
        primary_key=True
    )

    signature = models.CharField(max_length=50, default='I love grumblr!')
    age = models.IntegerField(validators=[MaxValueValidator(150), MinValueValidator(0)], default=0)

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')

    # the length limitation is set mainly for styling concerns in the template (aka "view" in MVC)
    hometown = models.CharField(max_length=15, default='Grumbland')
    hobby = models.CharField(max_length=15, default='Grumbling!')

    # a short bio of the user
    bio = models.CharField(max_length=420, default='A grumblr user.')

    # user avatar
    avatar = models.ImageField(upload_to=user_avatar_dir, default='defaults/default_avatar.png')

    # who this user is following
    following = models.ManyToManyField(
        User,
        related_name='followed_by'
    )
