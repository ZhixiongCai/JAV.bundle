# coding=utf-8

import datetime
from difflib import SequenceMatcher
import re

from bs4 import BeautifulSoup
import requests

from .base import ID_PATTERN, LibraryAgent


def with_default(default):
    def wrapper(func):
        def wrap(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                Log("JAVBus: " + e.with_traceback())
                return default
        return wrap
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
            ele = self.find_ele(soup, "識別碼:")
            bango = ele.find_all("span")[1].text.strip()
            title = self.get_original_title(soup)
        except AttributeError:
            Log("an exception occurred: " + url)
            return
        results.append(self.make_result(bango, title))
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
            "posters": self.get_posters(data),
            "art": self.get_thumbs(data)
        }

    @with_default("")
    def get_studio(self, data):
        ele = self.find_ele(data, "製作商:")
        if ele:
            return ele.find("a").text.strip()

    def get_original_title(self, data):
        title = data.find("div", "container").find("h3").text.strip()
        return title[title.find(' ') + 1:]

    @with_default(None)
    def get_originally_available_at(self, data):
        text = self.find_ele(data, "發行日期:").text
        match = re.search("\d+[-]\d+[-]\d+", text)
        return datetime.datetime.strptime(match.group(0), "%Y-%m-%d")

    @with_default([])
    def get_roles(self, data):
        return [
            {"name": e.text.strip()}
            for div in data.find("div", "movie").find("ul").find_all("div", "star-name")
            for e in div.find_all("a")
        ]

    @with_default(None)
    def get_duration(self, data):
        ele = self.find_ele(data, "長度:")
        match = re.search("\d+", ele.text)
        return int(match.group(0))*60*1000

    @with_default([])
    def get_directors(self, data):
        ele = self.find_ele(data, "導演:")
        return [{"name": ele.find("a").text.strip()}]

    @with_default([])
    def get_genres(self, data):
        return [
            span.find("a").text.strip()
            for span in data.find("div", "movie").find_all("span", "genre")
        ]

    @with_default(None)
    def get_posters(self, data):
        ele = data.find("a", "bigImage")
        link = "https://javbus.com" + ele["href"]
        return [link.replace("_b", "").replace("cover", "thumb")]

    @with_default(None)
    def get_thumbs(self, data):
        ele = data.find("a", "bigImage")
        link = "https://javbus.com" + ele["href"]
        return [link]

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
