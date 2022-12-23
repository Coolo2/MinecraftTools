
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from client import Client

import datetime

class CacheItem():
    def __init__(self, id : str, value):
        self.time = datetime.datetime.now()
        self.value = value
        self.id = id
    
    def __eq__(self, item):
        if item.id == self.id:
            return True 
        return False

class Cache():
    def __init__(self, timeout : datetime.timedelta = datetime.timedelta(hours=1)):
        self.cache : typing.List[CacheItem] = []
        self.timeout = timeout
    
    def add(self, id : str, value):
        item = CacheItem(id, value)

        if item in self.cache:
            self.cache.remove(item)
        self.cache.append(item)
    
    def get_by_id(self, id : str):
        removeIndex = None
        for item in self.cache:
            if item.id == id:
                if (datetime.datetime.now() - item.time) < self.timeout:
                    return item.value
                removeIndex = self.cache.index(item)
        
        if removeIndex:
            del self.cache[removeIndex]

        return None

class Caches():
    def __init__(self, client : Client):
        self.client = client 

        self.ResourceCache = Cache()
        self.SearchCache = Cache()