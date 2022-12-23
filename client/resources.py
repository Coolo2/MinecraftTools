
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from client import Client

import bs4 
import urllib.parse
import itertools
import os

class DownloadType:
    INTERNAL = "internal"
    EXTERNAL = "external"

class ResourceSite:
    SPIGOT = "spigot"
    BUKKIT = "bukkit"
    CURSEFORGE = "curseforge"

class Resources():
    def __init__(self, client : Client):
        self.client = client 
    
    async def search(self, query : str) -> typing.List[Resource]:
        result = self.client.caches.SearchCache.get_by_id(query)

        if not result:
            bukkit = await self._search_bukkit(query)
            spigot = await self._search_spigot(query)
            curseforge = await self._search_curseforge(query)

            result : typing.List[Resource] = [x for x in itertools.chain.from_iterable(itertools.zip_longest(bukkit,spigot,curseforge)) if x]
            names = [r.name for r in result]
            remove = []

            result.reverse()
            for resource in result:
                if names.count(resource.name) > 1 and resource.name not in [r.name for r in remove]:
                    remove.append(resource)
            result.reverse()

            for r in remove:
                del result[result.index(r)]

            self.client.caches.SearchCache.add(query, result)
            

        return result

    async def _search_bukkit(self, query : str):
        
        rs = []
        safe_query = urllib.parse.quote(query)
        t = await self.client.http.fetch_text("GET", f"https://dev.bukkit.org/search?search={safe_query}")

        soup = bs4.BeautifulSoup(t, features="html.parser")

        results = soup.find_all("tr", {"class": "results"})

        for result in results:

            name_html = result.find("div", {"class": "results-name"})
            name = name_html.find("a").contents[0]

            path = name_html.find("a", href=True)["href"]
            url = "https://dev.bukkit.org" + path

            id = int(path.replace("/projects/", ""))
            download_type = DownloadType.INTERNAL

            description = result.find("div", {"class": "results-summary"}).contents[0].strip()

            results_image = result.find("a", {"class":"results-image"})
            icon_url = results_image.find("img", src=True)["src"] if results_image.find("img") else None

            r = Resource(name, description, id, ResourceSite.BUKKIT, download_type, url, icon_url, api="bukkit")
            self.client.caches.ResourceCache.add(r.self_id, r)
            rs.append(r)
        
        
        return rs
    
    async def _search_spigot(self, query : str):
        rs = []
        safe_query = urllib.parse.quote(query)
        
        d = await self.client.http.fetch_json("GET", f"https://api.spiget.org/v2/search/resources/{safe_query}")
        for resource in d:

            file_type = DownloadType.INTERNAL
            if resource["file"]["type"] == "external":
                file_type = DownloadType.EXTERNAL
            path = "/".join(resource["file"]["url"].split("/")[:2]) # path is being uri encoded
            icon = ("https://www.spigotmc.org/" + resource["icon"]["url"]) if "icon" in resource else None
            if icon == "https://www.spigotmc.org/":
                icon = None
            
            r = Resource(
                name=resource["name"],
                description=resource["tag"],
                id=resource["id"],
                site=ResourceSite.SPIGOT,
                download_type=file_type,
                url=f"https://spigotmc.org/{path}",
                icon_url=icon,
                download_url=f"https://spigotmc.org/{path}/download?version={resource['version']['id']}",
                api="spigot",
                raw = resource
            )
            rs.append(r)
            self.client.caches.ResourceCache.add(r.self_id, r)
        
        return rs
    
    async def _search_curseforge(self, query : str):
        rs = []
        safe_query = urllib.parse.quote(query)

        headers={"x-api-key":os.getenv("curseforge"), "accept":"application/json"}

        d = await self.client.http.fetch_json("GET",
            f"https://api.curseforge.com/v1/mods/search?classId=5&sortField=6&sortOrder=desc&pageSize=50&searchFilter={safe_query}&gameId=432&index=0",
            headers=headers
        )
        for result in d["data"]:

            r = Resource(
                name=result["name"],
                description=result["summary"],
                id=result["id"],
                site=ResourceSite.CURSEFORGE,
                download_type=DownloadType.EXTERNAL,
                url=result["links"]["websiteUrl"],
                icon_url=result["logo"]["url"],
                download_url=result["links"]["websiteUrl"] + "/download",
                api="bukkit",
                raw=result
            )
            rs.append(r)
            self.client.caches.ResourceCache.add(r.self_id, r)
        
        return rs


class Resource():
    def __init__(self, name : str, description : str, id : int, site : ResourceSite, download_type : DownloadType, url : str, icon_url : str, download_url : str = None, api : str = None, raw : dict = None):
        self.name = name 
        self.description = description 
        self.id = id 
        self.site = site 
        self.download_type = download_type
        self.url = url
        self.icon_url = icon_url
        self._download_url = download_url
        self.api = api
        self.raw = raw

        self.self_id = self.site + "-" + str(self.id)
        self.redirect_url : str = None

        # Extra data 
        self.extra_data = False
        self.download_count : int = None
    
    async def fetch_extra_data(self, client : Client):
        self.extra_data = True
        if self.site == ResourceSite.CURSEFORGE:
            self.download_count = self.raw["downloadCount"]
        if self.site == ResourceSite.SPIGOT:
            self.download_count = self.raw["downloads"]
        if self.site == ResourceSite.BUKKIT:
            t = await client.http.fetch_text("GET", self.url)
            soup = bs4.BeautifulSoup(t, features="html.parser")
            before = soup.find("div", string="Total Downloads")
            self.download_count = int(before.find_next("div").string.replace(",", ""))

        client.caches.ResourceCache.add(self.self_id, self)
    
    async def get_download_url(self, client : Client):
        if self.site == ResourceSite.BUKKIT:
            if not self.redirect_url:
                self.redirect_url = await client.http.get_redirect(self.url)
            return str(self.redirect_url) + "/files/latest"
        else:
            return self._download_url


    def to_dict(self) -> dict:
        r = {
            "name":self.name,
            "description":self.description,
            "id":self.id,
            "site":self.site,
            "download_type":self.download_type,
            "url":self.url,
            "self_id":self.self_id,
            "icon_url":self.icon_url,
            "api":self.api,
            "extra":False
        }

        if self.extra_data:
            r["extra"] = True
            r["downloads"] = self.download_count

        return r
    
    def __eq__(self, other) -> bool:
        if self.site == other.site and self.id == other.id:
            return True 
        return False