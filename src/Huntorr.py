import logging
import os
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from qbittorrentapi import Client
from plexapi.server import PlexServer


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
            new_torrent = self.qb.torrents_add(urls=magnet_link, category="huntorr", use_auto_torrent_management=True, save_path="huntorr", seeding_time_limit=1440, is_first_last_piece_priority=True)
            if new_torrent == "Fails.":
                raise Exception("Failed to add torrent")

        except Exception as e:
            logger.error(str(e))


class Data_Handler:
    def __init__(self, media_server_addresses, media_server_tokens, media_server_library_name):
        self.media_server_addresses = media_server_addresses
        self.media_server_tokens = media_server_tokens
        self.media_server_library_name = media_server_library_name
        self.sites = [
            {"name": "1337X", "base_url": "https://1337x.to", "search_url": "https://1337x.to/search/", "query_space_replace": "+", "search_url_suffix": "/1/"},
            {"name": "EZTV", "base_url": "https://eztvx.to/", "search_url": "https://eztvx.to/search/", "query_space_replace": "-", "search_url_suffix": ""},
            {"name": "PB", "base_url": "https://thepiratebay0.org", "search_url": "https://thepiratebay0.org/search/", "query_space_replace": "%20", "search_url_suffix": "/1/99/0"},
            {"name": "OLD1", "base_url": "https://www1.thepiratebay3.to", "search_url": "https://www1.thepiratebay3.to/s/?q=", "query_space_replace": "+", "search_url_suffix": ""},
            {"name": "OLD2", "base_url": "https://1377x.to", "search_url": "https://1377x.to/search/", "query_space_replace": "+", "search_url_suffix": "/1/"},
        ]

    def getResults(self, query, selector):
        selectedSite = [element for element in self.sites if element["name"] == selector][0]
        site = selectedSite["name"]
        search_url = selectedSite["search_url"]
        q_s_r = selectedSite["query_space_replace"]
        search_url_suffix = selectedSite["search_url_suffix"]
        results = pd.DataFrame(columns=["Title", "Size", "Age", "Seeds", "Magnet"])

        h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"}
        url = search_url + query.replace(" ", q_s_r) + search_url_suffix

        if site == "EZTV":
            form_data = {"layout": "def_wlinks", "q_search_tv_packs_only": "off"}
            response = requests.post(url, headers=h, data=form_data)
            soup = BeautifulSoup(response.content, "lxml")
            tags = soup.find_all("tr", class_="forum_header_border")

        elif site == "1337X":
            try:
                flare_solverr_url = f"http://{torIP}:8191/v1"
                flare_solverr_data = {"cmd": "request.get", "url": url, "maxTimeout": 60000}
                flare_solverr_headers = {"Content-Type": "application/json"}
                flare_solverr_response = requests.post(flare_solverr_url, headers=flare_solverr_headers, json=flare_solverr_data)

                if flare_solverr_response.status_code == 200:
                    soup = BeautifulSoup(flare_solverr_response.content, "lxml")
                    tags = soup.find_all("tr")[1:]
                else:
                    raise Exception("FlareSolverr failed, falling back to regular request")
            except Exception as e:
                logger.error(f"Error using FlareSolverr: {str(e)}")
                response = requests.get(url, headers=h)
                soup = BeautifulSoup(response.content, "lxml")
                tags = soup.find_all("tr")[1:]

        else:
            response = requests.get(url, headers=h)
            soup = BeautifulSoup(response.content, "lxml")
            tags = soup.find_all("tr")[1:]

        for tag in tags:
            try:
                r_hol = self.parseResult(site, tag)
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

    def parseResult(self, site, tag):
        result = None
        title = None
        magnet = None
        size = None
        age = None
        seeds = None
        if site == "EZTV":
            title = tag.contents[3].a.text
            magnet = tag.contents[5].find_all(class_="magnet")[0]["href"]
            age = tag.contents[9].text
            size = tag.contents[7].text
            seeds = int(tag.contents[11].text.replace(",", "").replace("-", "0"))

            result = {
                "Title": title,
                "Magnet": magnet,
                "Size": size,
                "Age": age,
                "Seeds": seeds,
            }

        elif site == "1337X":
            title = tag.contents[1].text[1:]
            size = tag.contents[9].text
            age = tag.contents[7].text
            seeds = int(tag.contents[3].text.replace(",", "").replace("-", "0"))
            result = {
                "Title": title,
                "Size": size,
                "Age": age,
                "Seeds": seeds,
            }

            # Open and parse search links
            selectedBaseSite = [element for element in self.sites if element["name"] == site][0]
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
            title = tag.contents[3].contents[1].text[:-1]
            magnet = tag.contents[3].contents[3]["href"]

            try:
                size = tag.contents[3].contents[7].text.split(",")[1].replace("\xa0", " ")[6:]
            except:
                size = tag.contents[3].contents[6].text.split(",")[1].replace("\xa0", " ")[6:]

            try:
                age = tag.contents[3].contents[7].text.split(",")[0].replace("\xa0", " ").split("Uploaded")[1][1:]
            except:
                age = tag.contents[3].contents[6].text.split(",")[0].replace("\xa0", " ").split("Uploaded")[1][1:]

            try:
                seeds = int(tag.contents[5].text.replace(",", "").replace("-", "0"))
            except:
                seeds = int(tag.contents[5].text.replace(",", "").replace("-", "0"))

            result = {
                "Title": title,
                "Magnet": magnet,
                "Size": size,
                "Age": age,
                "Seeds": seeds,
            }

        elif site == "OLD":
            title = tag.contents[3].text[:-2]
            size = tag.contents[9].text
            age = tag.contents[5].text
            seeds = int(tag.contents[11].text.replace(",", "").replace("-", "0"))
            result = {
                "Title": title,
                "Size": size,
                "Age": age,
                "Seeds": seeds,
            }

            selectedBaseSite = [element for element in self.sites if element["name"] == site][0]
            base_url = selectedBaseSite["base_url"]
            h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"}
            download_url = tag.contents[3].find_all("a")[0]["href"]
            req_tmp = requests.get(base_url + download_url, headers=h)
            c_tmp = req_tmp.content
            soup_tmp = BeautifulSoup(c_tmp, "lxml")

            magnet_str = str(soup_tmp.find_all(class_="download")[0].contents[1])
            result["Magnet"] = magnet_str.split(sep='"')[1]

        return result

    def finder(self, query, selector):
        if selector not in [element["name"] for element in self.sites]:
            selector = self.sites[0]["name"]
        results = self.getResults(query, selector)
        return results

    def convert_string_to_dict(self, raw_string):
        result = {}
        if not raw_string:
            return result

        pairs = raw_string.split(",")
        for pair in pairs:
            key_value = pair.split(":", 1)
            if len(key_value) == 2:
                key, value = key_value
                result[key.strip()] = value.strip()

        return result

    def save_settings(self, data):
        self.media_server_addresses = data["media_server_addresses"]
        self.media_server_tokens = data["media_server_tokens"]
        self.media_server_library_name = data["media_server_library_name"]

    def sync_media_servers(self):
        media_servers = self.convert_string_to_dict(media_server_addresses)
        media_tokens = self.convert_string_to_dict(media_server_tokens)

        plex_status = "Not required"
        jellyfin_status = "Not required"

        if "Plex" in media_servers and "Plex" in media_tokens:
            try:
                token = media_tokens.get("Plex")
                address = media_servers.get("Plex")
                logger.warning("Attempting Plex Sync")
                media_server_server = PlexServer(address, token)
                library_section = media_server_server.library.section(media_server_library_name)
                library_section.update()
                logger.warning(f"Plex Library scan for '{media_server_library_name}' started.")
                plex_status = "Success"
            except Exception as e:
                logger.warning(f"Plex Library scan failed: {str(e)}")
                plex_status = "Failed"

        if "Jellyfin" in media_tokens and "Jellyfin" in media_tokens:
            try:
                token = media_tokens.get("Jellyfin")
                address = media_servers.get("Jellyfin")
                logger.warning("Attempting Jellyfin Sync")
                url = f"{address}/Library/Refresh?api_key={token}"
                response = requests.post(url)
                if response.status_code == 204:
                    logger.warning("Jellyfin Library refresh request successful.")
                    jellyfin_status = "Success"
                else:
                    logger.warning(f"Jellyfin Error: {response.status_code}, {response.text}")
                    jellyfin_status = "Failed"
            except Exception as e:
                logger.warning(f"Jellyfin Library scan failed: {str(e)}")
                jellyfin_status = "Failed"

        return f"Plex status: {plex_status}, Jellyfin status: {jellyfin_status}"


app = Flask(__name__)
app.secret_key = "secret_key"

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()

torUserName = os.environ.get("torrenter_username", "pi")
torPassword = os.environ.get("torrenter_password", "raspberry")
torIP = os.environ.get("torrenter_ip", "192.168.1.2")
torPort = os.environ.get("torrenter_port", "5678")
torAddress = "http://" + torIP + ":" + torPort
qbit = QBittorrentAPI(torAddress, torUserName, torPassword)

media_server_addresses = os.environ.get("media_server_addresses", "Plex: http://192.168.1.2:32400, Jellyfin: http://192.168.1.2:8096")
media_server_tokens = os.environ.get("media_server_tokens", "Plex: abc, Jellyfin: xyz")
media_server_library_name = os.environ.get("media_server_library_name", "Movies")
data_handler = Data_Handler(media_server_addresses, media_server_tokens, media_server_library_name)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("base.html")


@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    searchText = data["input"]
    searchEngine = data["engine"]
    qbit.results = data_handler.finder(searchText, searchEngine)
    choppedResults = qbit.results[["Title", "Age", "Size", "Seeds"]]
    newTableHMTL = choppedResults.to_html(classes="tableStyle table table-hover table-striped table-bordered", table_id="resultsTable", header="true", justify="center")
    return {"table": newTableHMTL}


@app.route("/send_magnet", methods=["POST"])
def send_magnet():
    try:
        data = request.get_json()
        dl_choice = int(data["choice"])
        qbit.connect()
        qbit.add_new(dl_choice)
    except Exception as e:
        logger.error(str(e))
        return {"Status": "Error: Failed to add magnet - Check Logs"}
    else:
        return {"Status": "Success: Magnet Added"}


@app.route("/refresh_media_server", methods=["POST"])
def refresh_media_server():
    try:
        result = data_handler.sync_media_servers()
    except Exception as e:
        logger.error(str(e))
        return {"Status": "Error - Check Logs"}
    return {"Status": result}


@app.route("/save_settings", methods=["POST"])
def save_settings():
    try:
        data = request.get_json()
        data_handler.save_settings(data)
    except Exception as e:
        logger.error(str(e))
        return {"Status": "Error: Check Logs"}
    else:
        return {"Status": "Success: Settings Saved"}


@app.route("/load_settings", methods=["GET"])
def load_settings():
    data = {
        "media_server_addresses": data_handler.media_server_addresses,
        "media_server_tokens": data_handler.media_server_tokens,
        "media_server_library_name": data_handler.media_server_library_name,
    }
    return data


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000)
