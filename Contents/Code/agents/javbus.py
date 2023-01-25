# coding=utf-8

import datetime
from difflib import SequenceMatcher
import re

from bs4 import BeautifulSoup
import requests

from .base import ID_PATTERN, LibraryAgent


    def with_default(default):
        def wrapper(func):
            def _func(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except:
                    return default
            return _func
        return wrapper

class JAVBus(LibraryAgent):
    def get_name(self):
        return "JAVBus"

    def guess_keywords(self, name):
        match = re.search(ID_PATTERN, name)
        if match:
            return [match.group(1).upper()]
        return []

    def query(self, keyword):
        keyword = keyword.upper()
        results = []
        url = "https://www.javbus.com/" + keyword
        resp = self.session.get(url)
        resp.raise_for_status()
        html = resp.content.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        try:
            bango = soup.find("div", "movie").find_all("p")[0].find_all("span")[1].text.strip()
        except AttributeError:
            Log("an exception occurred: " + url)
            return
        results.append(self.make_result(
            bango,
            bango
        ))
        return results

    def get_metadata(self, metadata_id):
        agent_id = self.get_agent_id(metadata_id)
        data = self.crawl(agent_id)

        title = self.get_original_title(data)
        if not title:
            raise Exception(
                "Got an unexpected response for {0}".format(metadata_id))

        return {
            "movie_id": re.split(r"\s", title)[0],
            "agent_id": agent_id,
            "title": title,
            "originally_available_at": self.get_originally_available_at(data),
            "roles": self.get_roles(data),
            "directors": self.get_directors(data),
            "studio": self.get_studio(data),
            "duration": self.get_duration(data),
            "genres": self.get_genres(data),
            "rating": self.get_rating(data),
            "posters": self.get_posters(data),
            "art": self.get_thumbs(data)
        }

    def get_studio(self, data):
        ele = self.find_ele(data, "製作商:")
        if ele:
            return ele.
        return data.find("div", "movie").find_all("p")[3].find("a").text.strip()

    def get_original_title(self, data):
        title = soup.find("div", "container").find("h3").text.strip()
        return title[title.find(' ') + 1:]

    def get_originally_available_at(self, data):
        text = soup.find("div", "movie").find_all("p")[1].text
        match = re.search("\d+[-]\d+[-]\d+", text)
        try:
            if match:
                return datetime.datetime.strptime(match.group(0), "%Y-%m-%d")
        except ValueError:
            pass

    def get_roles(self, data):
        return [
            {"name": e.text.strip()}
            for div in soup.find("div", "movie").find("ul").find_all("div", "star-name")
            for e in div.find_all("a")
        ]

    def get_duration(self, data):
        match = re.search("\d+", soup.find("div", "movie").find_all("p")[2].text)
        return int(match.group(0))*60*1000

    def get_directors(self, data):
        ele = self.find_ele(data, "監督:")
        if ele and ele.find("a"):
            return [{"name": ele.find("a").text.strip()}]
        return []

    def get_genres(self, data):
        ele = self.find_ele(data, "ジャンル:")
        if ele:
            return [ele.text.strip() for ele in ele.findAll("a")]
        return []

    def get_rating(self, data):
        ele = self.find_ele(data, "平均評価:")
        if ele:
            try:
                return float(ele.find("span", "score").text.strip("()"))
            except ValueError:
                pass

    def get_posters(self, data):
        javlibrary_thumb = data.find("img", {"id": "video_jacket_img"})
        if javlibrary_thumb and javlibrary_thumb["src"]:
            src = javlibrary_thumb["src"]
            if not src.startswith("http"):
                src = "https:" + src
            return [src.replace("pl.", "ps.")]

    def get_thumbs(self, data):
        javlibrary_thumb = data.find("img", {"id": "video_jacket_img"})
        if javlibrary_thumb and javlibrary_thumb["src"]:
            src = javlibrary_thumb["src"]
            if not src.startswith("http"):
                src = "https:" + src
            return [src]

    def crawl(self, agent_id):
        url = "https://www.javbus.com/" + agent_id
        resp = self.session.get(url)
        resp.raise_for_status()
        html = resp.content.decode("utf-8")
        return BeautifulSoup(html, "html.parser")

    def find_ele(self, data, title):
        ele = data.find("div", "movie")
        single_infos = ele.findAll("p")
        for single_info in single_infos:
            if single_info.find("span").text.strip() == title:
                return single_info

      
      
    s_requests = None
    s_cloudscraper = None

    @property
    def session(self):
        if not self.s_requests:
            self.s_requests = requests.session()
            if Prefs["userAgent"]:
                self.s_requests.headers["User-Agent"] = Prefs["userAgent"]
        return self.s_requests
