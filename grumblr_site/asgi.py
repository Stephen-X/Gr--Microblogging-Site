"""
ASGI entrypoint file for default channel layer.
"""

import os
from channels.asgi import get_channel_layer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grumblr_site.settings")
channel_layer = get_channel_layer()
