"""
Global models for the grumblr site.

Unfortunately we have to create a separate app for global models instead of putting
it in the project directory ("grumblr_site"), as models can only be recognized by
editing the "INSTALLED_APPS" setting.

Remember to run <code>manage.py migrate</code> every time this file is modified.

Author: Stephen Xie <[redacted]@cmu.edu>
Version: 1.2.0
"""
import json
import logging

from channels import Group
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

# for printing debugging info to console
logger = logging.getLogger(__name__)


class Message(models.Model):
    """
    The message model.
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

    @property
    def html(self):
        """
        A Python property used to return a bootstrap card HTML code representation
        of the current message. To access it, simply treat this "method" as an
        attribute of the message (i.e. message.html).

        :return: an HTML code representation of the current message for Django template
        """
        # profile url of this user will be something like /profile/username
        profile_url = reverse('profile') + self.user.username
        return """
        <div class='card msg-card'>
            <div class='card-body'>
                <div class='row no-gutters align-items-start'>
                    <a href='{0}' class='col-auto'>
                        <img class='avatar' src='{1}' alt='avatar'>
                    </a>
        
                    <div class='col'>
                        <div class='row no-gutters'>
                            <div class='col'>
                                <a href='{0}'>
                                    <h4 class='card-title'>{2} {3}</h4>
                                </a>
                            </div>
                            <div class='col-5 date'>{4}</div>
                        </div>
        
                        <div class='row no-gutters'>
                            <p class='card-text'>{5}</p>
                        </div>
        
                        <!-- message card function bar -->
                        <div class='row no-gutters func-bar'>
                            <div class='col-2'>
                                <a class='btn btn-default btn-sm' href='#'>
                                    <i class='fa fa-heart'></i> LIKE</a>
                            </div>
                            <div class='col-2'>
                                <a class='btn btn-default btn-sm' href='#'>
                                    <i class='fa fa-retweet fa-lg'></i> SHARE</a>
                            </div>
                        </div>
        
                        <div class='comment-field'>
                            <!-- comment input field -->
                            <div class='row no-gutters align-items-center input-group'>
                                <!-- HTML form is not required here, as the posting logic is handled by comments_control.js -->
                                <input class='form-control comment-input' type='text' name='comment' maxlength='42' placeholder='Comment this post' required>
                                <span class='input-group-btn'>
                                    <button class='btn btn-secondary comment-sent-btn' type='submit'>Send!</button>
                                </span>
                            </div>
                            <div class='comment-list'>{6}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """.strip().format(profile_url, self.user.ext.avatar.url, self.user.first_name, self.user.last_name,
                           self.date.strftime('%H:%M %p - %d %b %Y'), self.message,
                           '\n'.join([c.html for c in Comment.get_all_ranged(self)]))
        # note that the original curly braces used for Django template need to be escape like this: '{{' and '}}'
        # before python string formatter can be used
        # '%H:%M %p - %d %b %Y' example: 9:05 PM - 19 Oct 2017
        # Python strftime ref: http://strftime.org/

    # override the save method to send real-time message updates to the global_stream group
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # send the trade record to the group; all consumers (aka "listeners") to that group
        # will be notified
        # WebSocket text frame, with JSON content
        Group('global_stream').send({
            'text': json.dumps({
                'id': self.id,
                'author': self.user.username,
                'html': self.html
            })
        })

    @staticmethod
    def get_all_ranged(mrange=20, offset=0, from_date='1970-01-01T00:00+00:00'):
        """
        Get a range of messages from all the records in the database,
        sorted in chronological order. The method is designed for
        pagination in messages display.

        :param mrange: how many messages will be returned
        :param offset: index of the first message in the list (0-based)
        :param from_date:
        :return: a range of ordered messages
        """
        return Message.objects.filter(date__gt=from_date).order_by('date')[offset:offset + mrange]

    @staticmethod
    def get_user_ranged(user, mrange=20, offset=0, from_date='1970-01-01T00:00+00:00'):
        """
        Get a range of messages from all the records of the given user,
        sorted in chronological order. The method is designed for
        pagination in messages display.

        :param user: the given user
        :param mrange: how many messages will be returned
        :param offset: index of the first message in the list (0-based)
        :param from_date:
        :return: a range of ordered messages
        """
        return Message.objects.filter(user=user, date__gt=from_date).order_by('date')[offset:offset+mrange]

    @staticmethod
    def get_followers_ranged(user, mrange=20, offset=0, from_date='1970-01-01T00:00+00:00'):
        """
        Get a range of messages from all the records of users this current
        user is following, sorted in chronological order.
        The method is designed for pagination in messages display.

        :param user: user who the followers follow
        :param mrange: how many messages will be returned
        :param offset: index of the first message in the list (0-based)
        :param from_date:
        :return: a range of ordered messages
        """
        # first get all followers
        followers = user.ext.following.all()
        # then search and sort
        return Message.objects.filter(user__in=followers, date__gt=from_date).order_by('date')[offset:offset+mrange]


def user_avatar_dir(instance, filename):
    """
    Helper functions for determining file upload locations.
    Files will be uploaded to [MEDIA_ROOT]/user_<id>/avatar/<filename>
    :param instance: an instance of the model where the ImageField is defined
    :param filename: the filename that was originally given to the file
    :return: the file path to be uploaded to
    """
    return 'user_{0}/avatar/{1}'.format(instance.user.id, filename)


class Comment(models.Model):
    """
    The comment model.
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='cmts'  # Comment fields can now be accessed from the Message object via message.cmt
    )
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=42)

    @property
    def html(self):
        """
        A Python property used to return a bootstrap card HTML code representation
        of the current comment. To access it, simply treat this "method" as an
        attribute of the comment (i.e. comment.html).

        :return: an HTML code representation of the current comment for Django template
        """
        # profile url of this user will be something like /profile/username
        profile_url = reverse('profile') + self.from_user.username
        return """
        <div class='row no-gutters comment'>
            <div class='avatar-col'>
                <a href='{0}' class='col-auto'>
                    <img class='avatar' src='{1}' alt='avatar'>
                </a>
            </div>
            <div class='text-col'>
                <div class='row no-gutters title'>
                    <a href='{0}' class='col-7 name'>{2} {3} ({4})</a>
                    <div class='col-5 date'>{5}</div>
                </div>
                <div class='row no-gutters'>{6}</div>
            </div>
        </div>
        """.strip().format(profile_url, self.from_user.ext.avatar.url, self.from_user.first_name,
                           self.from_user.last_name, self.from_user.username,
                           self.date.strftime('%H:%M %p - %d %b %Y'), self.content)

    @staticmethod
    def get_all_ranged(message, mrange=20, offset=0, from_date='1970-01-01T00:00+00:00'):
        """
        Get a range of latest comments starting from a given time period to
        a specified message in the database, sorted in chronological order.
        The method is designed for pagination.

        :param message: the given message
        :param mrange: how many comments will be returned
        :param offset: index of the first message in the list (0-based)
        :param from_date:
        :return: a range of ordered comments
        """
        return Comment.objects.filter(message=message, date__gt=from_date).order_by('date')[offset:offset + mrange]


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
