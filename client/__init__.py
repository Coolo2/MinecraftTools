
from client import http, resources, cache

from client.resources import Resource

import typing
import urllib.parse

class Client():
    def __init__(self):
        
        self.caches = cache.Caches(self)
        self.http = http.HTTP(self)
        self.resources = resources.Resources(self)

