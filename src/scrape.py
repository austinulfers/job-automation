import urllib3
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import json
import os
import re

CONFIG = "config.json"
CWD = os.getcwd()

class Craigslist:
    """This class scrapes Cragslist for listing given preferences.
    """    
    def __init__(self):
        json = read_json(CONFIG)
        self.pref = json["PREFERENCES"]
    
    def run(self):
        """Performs the actual scraping operations. Kept seperate to make
        debugging easier.
        """
        text_bodies = []
        contacts = []
        for city in self.pref["CITIES"]:
            assert isinstance(city, str)
            city = city.lower()
            header = city + ".craigslist.org/d/computer-gigs/search/cpg"
            html = scrape(header)
            headers, posts = self.get_postings(html)
            assert len(headers)==len(posts), "title and post length mismatch"
            for post in posts:
                html = scrape(post)
                text_bodies.append(self.get_post_body(html))
        export = pd.DataFrame({
            "body": text_bodies,
            "title": headers,
            "url":posts
        })
        export.to_csv("export.csv")

    def get_post_contact(self, html: str) -> str:
        raise NotImplementedError

    def get_post_body(self, html: str) -> str: 
        """Gets a post's text body.

        Args:
        html (str): the html of the post page

        Returns:
            str: the post body
        """        
        soup = BeautifulSoup(html, "html.parser")
        body = soup.find(id="postingbody")
        return body.get_text()

    def get_postings(self, html: str) -> list:
        """Yields the posting information from the query page.

        Args:
            html (str): the search page html 

        Returns:
        list: all the posting urls
        """        
        soup = BeautifulSoup(html, "html.parser")
        results = soup.find(id="sortable-results")
        postings = results.find_all("a")
        headers = [i.text.replace("\n", "") for i in postings]
        exclude = ["", "restorerestore this posting"]
        headers = [i for i in headers if i not in exclude]
        yield headers
        posting_urls = [post.get("href") for post in postings if post.text in headers]
        yield posting_urls

def scrape(url: str) -> str:
    """Returns the html as a string of a url.

    Args:
        url (str): url to scrape

    Returns:
        str: html content of the webpage
    """    
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    return r.data

def read_json(path: str) -> dict:
    """Returns data stored in a json file.

    Args:
        path (str): path to the json file

    Returns:
        dict: contents of the json file
    """    
    with open(path) as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    auto = Craigslist()
    auto.run()