"""
Defines how consumers (those who listen to the channel) interacts with the
grumbles (messages) stream channel.

Author: Stephen Xie <[redacted]@cmu.edu>
"""
from channels import Group


def connect_global_stream(message):
    """
    When the user opens a WebSocket to a global stream, adds them to the
    group for that stream so they receive new message updates.

    The updates are actually sent in the Message model on save.
    """
    # accept the incoming connection
    message.reply_channel.send({'accept': True})
    # add the reply_channel of this connection to the global_stream group,
    # so that it can receive updates sent to the group (all group members
    # will be able to get the same message)
    Group('global_stream').add(message.reply_channel)


def disconnect_global_stream(message):
    """
    Removes the user from the global_stream group when they disconnect.

    Channels will auto-cleanup eventually, but it can take a while, and having old
    entries cluttering up the group will reduce performance.
    """
    Group('global_stream').discard(message.reply_channel)
