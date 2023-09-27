import logging
import os
import sys
import traceback
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request
from qbittorrentapi import Client


class QBittorrentAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.results = None

    def connect(self):
        try:
            self.qb = Client(host=self.base_url, username=self.username, password=self.password)
            self.qb.auth_log_in()
        except Exception as e:
            logger.error(str(e))
            raise Exception(str(e))

    def get_list(self):
        try:
            torrents = None
            torrents = self.qb.torrents_info()

        except Exception as e:
            logger.error(str(e))

        return torrents

    def add_new(self, dl_choice):
        try:
            magnet_link = self.results["Magnet"].loc[dl_choice]
            new_torrent = self.qb.torrents_add(urls=magnet_link)
        except Exception as e:
            logger.error(str(e))


app = Flask(__name__)
app.secret_key = "secret_key"
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()

torUserName = "admin"  # os.environ["torrenter_username"]
torPassword = "abcRaspberry123"  # os.environ["torrenter_password"]
torIP = "192.168.1.222"  # os.environ["torrenter_ip"]
torPort = "5001"  # os.environ["torrenter_port"]
torAddress = "http://" + torIP + ":" + torPort

qbit = QBittorrentAPI(torAddress, torUserName, torPassword)

sites = [
    {"name": "1377X", "base_url": "https://1377x.to", "search_url": "https://1377x.to/search/", "query_space_replace": "%20", "search_url_suffix": "/1/"},
    {"name": "EZTV", "base_url": "https://eztv.ag", "search_url": "https://eztv.ag/search/", "query_space_replace": "-", "search_url_suffix": ""},
    {"name": "PB", "base_url": "https://thepiratebay0.org", "search_url": "https://thepiratebay0.org/search/", "query_space_replace": "%20", "search_url_suffix": "/1/99/0"},
    {"name": "OLD", "base_url": "https://www1.thepiratebay3.to", "search_url": "https://www1.thepiratebay3.to/s/?q=", "query_space_replace": "+", "search_url_suffix": ""},
]


def getResults(query, selector):
    selectedSite = [element for element in sites if element["name"] == selector][0]
    site = selectedSite["name"]
    search_url = selectedSite["search_url"]
    q_s_r = selectedSite["query_space_replace"]
    search_url_suffix = selectedSite["search_url_suffix"]
    results = pd.DataFrame(columns=["Title", "Size", "Age", "Seeds", "Magnet"])

    h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"}
    url = search_url + query.replace(" ", q_s_r) + search_url_suffix
    req = requests.get(search_url + query.replace(" ", q_s_r) + search_url_suffix, headers=h)
    c = req.content
    soup = BeautifulSoup(c, "lxml")

    if site == sites[0]["name"]:
        tags = soup.find_all("tr")[1:]
    elif site == sites[1]["name"]:
        tags = soup.find_all("tr", class_="forum_header_border")
    elif site == sites[2]["name"]:
        tags = soup.find_all("tr")[1:]
    elif site == sites[3]["name"]:
        tags = soup.find_all("tr")[1:]

    for tag in tags:
        try:
            r_hol = parseResult(site, tag)
            if r_hol:
                new_r_hol = pd.DataFrame([r_hol])
            else:
                new_r_hol = None
            results = pd.concat([results, new_r_hol], axis=0, ignore_index=True)
        except Exception as e:
            logger.error(str(e))

    results["Seeds"] = pd.to_numeric(results["Seeds"], downcast="integer")
    results.sort_values(["Seeds", "Age"], axis=0, ascending=[False, False], inplace=True)
    results = results.reset_index(drop=True)
    return results


def parseResult(site, tag):
    result = None
    if site == "EZTV":
        result = {
            "Title": tag.contents[3].a.text,
            "Magnet": tag.contents[5].find_all(class_="magnet")[0]["href"],
            "Size": tag.contents[7].text,
            "Age": tag.contents[9].text,
            "Seeds": int(tag.contents[11].text.replace(",", "").replace("-", "0")),
        }

    elif site == "1377X":
        result = {
            "Title": tag.contents[1].text[1:],
            "Size": tag.contents[9].text,
            "Age": tag.contents[7].text,
            "Seeds": int(tag.contents[3].text.replace(",", "").replace("-", "0")),
        }

        # Open and parse search links
        selectedBaseSite = [element for element in sites if element["name"] == site][0]
        base_url = selectedBaseSite["base_url"]
        h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"}
        download_url = tag.contents[1].find_all("a")[1]["href"]
        req_tmp = requests.get(base_url + download_url, headers=h)
        c_tmp = req_tmp.content
        soup_tmp = BeautifulSoup(c_tmp, "lxml")
        magnet_str = soup_tmp.select('a[href^="magnet"]')
        magnet_str = magnet_str[0]["href"] if magnet_str else None
        result["Magnet"] = magnet_str

    elif site == "PB":
        result = {
            "Title": tag.contents[3].contents[1].text[:-1],
            "Magnet": tag.contents[3].contents[3]["href"],
            "Size": tag.contents[3].contents[7].text.split(",")[1].replace("\xa0", " ")[6:],
            "Age": tag.contents[3].contents[7].text.split(",")[0].replace("\xa0", " ").split("Uploaded")[1][1:],
            "Seeds": int(tag.contents[5].text.replace(",", "").replace("-", "0")),
        }

    elif site == "OLD":
        result = {
            "Title": tag.contents[3].text[:-2],
            "Size": tag.contents[9].text,
            "Age": tag.contents[5].text,
            "Seeds": int(tag.contents[11].text.replace(",", "").replace("-", "0")),
        }

        selectedBaseSite = [element for element in sites if element["name"] == site][0]
        base_url = selectedBaseSite["base_url"]
        h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"}
        download_url = tag.contents[3].find_all("a")[0]["href"]
        req_tmp = requests.get(base_url + download_url, headers=h)
        c_tmp = req_tmp.content
        soup_tmp = BeautifulSoup(c_tmp, "lxml")

        magnet_str = str(soup_tmp.find_all(class_="download")[0].contents[1])
        result["Magnet"] = magnet_str.split(sep='"')[1]

    return result


def finder(query, selector):
    if selector not in [element["name"] for element in sites]:
        selector = sites[0]["name"]
    results = getResults(query, selector)
    return results


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("base.html")


@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    searchText = data["input"]
    searchEngine = data["engine"]
    qbit.results = finder(searchText, searchEngine)
    choppedResults = qbit.results[["Title", "Age", "Size", "Seeds"]]
    newTableHMTL = choppedResults.to_html(classes="tableStyle", table_id="resultsTable", header="true", justify="center")
    return {"table": newTableHMTL}


@app.route("/send_magnet", methods=["POST"])
def send_magnet():
    data = request.get_json()
    try:
        dl_choice = int(data["choice"])
        qbit.connect()
        qbit.add_new(dl_choice)
    except Exception as e:
        logger.error(str(e))
        return {"Status": "Error: " + str(e)}
    else:
        return {"Status": "Success: Magnet Added"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
