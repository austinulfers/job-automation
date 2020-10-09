import urllib3
from bs4 import BeautifulSoup
import pandas as pd

class Craigslist:
    
    def __init__(self, url: str):
        self.url = url
    
    def run(self):
        data = self.scrape()
        self.parse(data)

    def scrape(self) -> str:
        http = urllib3.PoolManager()
        r = http.request("GET", self.url)
        return r.data

    def parse(self, raw: str):
        soup = BeautifulSoup(raw, "html.parser")
        print(soup.find(id="sortable-results"))


if __name__ == "__main__":
    auto = Craigslist("https://seattle.craigslist.org/search/jjj?query=developer")
    auto.run()