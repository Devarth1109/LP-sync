# LPsync/routing.py
from django.urls import re_path
from LPsyncAdmin.consumers import ScrapeConsumer

websocket_urlpatterns = [
    re_path(r'ws/sitemap/(?P<sitemap_id>\d+)/scrape/$', ScrapeConsumer.as_asgi()),
]