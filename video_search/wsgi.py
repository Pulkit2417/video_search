"""
WSGI config for video_search project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from dj_static import Cling, MediaCling
from static_ranges import Ranges
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

"""class CustomWhiteNoise(WhiteNoise):
    def mimetype(self, path, url):
        if path.endswith('.vtt'):
            return 'text/vtt'
        return super().mimetype(path, url)
"""

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_search.settings')
#application = Ranges(CustomWhiteNoise(Cling(MediaCling(get_wsgi_application()))))

application = Ranges(Cling(MediaCling(get_wsgi_application())))
#application = get_wsgi_application()
