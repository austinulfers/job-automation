import urllib3
from bs4 import BeautifulSoup
import pandas as pd
import json
import os

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
        debuggin easier.
        """
        text_bodies = []
        contacts = []
        for city in self.pref["CITIES"]:
            assert isinstance(city, str)
            city = city.lower()
            header = city + ".craigslist.org/search/"
            for category in self.pref["CATEGORIES"]:
                assert isinstance(category, str)
                category = category.lower()
                queries = "?query=" + "+".join(self.pref["KEYWORDS"])
                url = header + category + queries
                html = scrape(url)
                posts = self.get_postings(html)
                posts = [x for x in posts if x.startswith("https://" + city)]
                posts = list(set(posts))
                for post in posts:
                    html = scrape(post)
                    text_bodies.append(self.get_post_body(html))
                    # contacts.append(self.get_post_contact(html))
        export = pd.DataFrame(
            data=text_bodies, 
            columns=["body"]
        )
        export.to_csv("export.csv")

    def get_post_contact(self, html: str) -> str:
        raise NotImplementedError

    def get_post_body(self, html: str) -> str:
        """Gets a post's text body.

        Parameters
        ----------
        html : str
            the html of the post page

        Returns
        -------
        str
            the post body
        """        
        soup = BeautifulSoup(html, "html.parser")
        body = soup.find(id="postingbody")
        return body.get_text()

    def get_postings(self, html: str) -> list:
        """Returns the postings urls from the query page.

        Parameters
        ----------
        html : str
            the search page html 

        Returns
        -------
        list
            all the posting urls
        """        
        soup = BeautifulSoup(html, "html.parser")
        results = soup.find(id="sortable-results")
        postings = results.find_all("a")
        posting_urls = [post.get("href") for post in postings]
        posting_urls = [post for post in posting_urls if post != "#"]
        return posting_urls

def scrape(url: str) -> str:
    """Returns the html as a string of a url.

    Parameters
    ----------
    url : str
        url to scrape

    Returns
    -------
    str
        html content of the webpage
    """    
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    return r.data

def read_json(path: str) -> dict:
    """Returns data stored in a json file.

    Parameters
    ----------
    path : str
        path to the json file

    Returns
    -------
    dict
        contents of the json file
    """    
    with open(path) as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    auto = Craigslist()
    auto.run()