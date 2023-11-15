import re
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from database import  detect_duplicates
from tqdm import tqdm  # Import tqdm for the progress bar
import random
from Config.config import Config
from Config.logs_config import setup_logging, process_browser_log_entry
from Driver.driver_config import driver_setup
from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions
from database import find_anime
import subprocess
from AnimeWatcher.FileOperations import FileOperations
import json
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter, Retry
from Cryptodome.Cipher import AES
from urllib.parse import urlparse, parse_qsl, urlencode, urljoin
import base64
from pathlib import Path
import m3u8
import os

from python_mpv_jsonipc import MPV

logger = setup_logging('anime_watch', Config.ANIME_WATCH_LOG_PATH)
    
class AnimeWatch:
    def __init__(self, web_interactions=None, anime_interactions=None, quality=None):
        self.web_interactions = web_interactions if web_interactions else WebInteractions()
        self.anime_interactions = anime_interactions if anime_interactions else AnimeInteractions()
        self.file_operations = FileOperations()
        
        self.session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.ajax_url = "/encrypt-ajax.php?"
        self.enc_key_api = "https://raw.githubusercontent.com/justfoolingaround/animdl-provider-benchmarks/master/api/gogoanime.json"
        self.mode = AES.MODE_CBC
        self.size = AES.block_size
        self.padder = "\x08\x0e\x03\x08\t\x03\x04\t"
        self.pad = lambda s: s + chr(len(s) % 16) * (16 - len(s) % 16)
        
        self.qual = quality.lower().strip("p") # quality of the video
        
    def naviguate_fetch_episodes(self, url):
        try:
            self.web_interactions.naviguate(url)
            # find the episode list
            start_episode, max_episode = self.anime_interactions.get_number_episodes()
            prompt = input(f"Enter the episode you want to start watching between {start_episode}-{max_episode} (or 0 to exit): ")
            if prompt == '0':
                print("Exiting...")
                return
            if prompt.isdigit() and start_episode <= int(prompt) <= max_episode:
                anime_name = self.anime_interactions.format_anime_name_url(url)
                self.web_interactions.naviguate(self.anime_interactions.format_episode_link(prompt, anime_name))
                
                ep_url = self.embed_url(self.anime_interactions.format_episode_link(prompt, anime_name))
                print("ep_url", ep_url)
                self.stream_url(ep_url)
                #self.embed_url(self.anime_interactions.format_episode_link(prompt, anime_name))
            else:
                print("Invalid input. Please enter a valid episode.")
                self.naviguate_fetch_episodes(url)
            #self.logs_of_webdriver(self.web_interactions.driver)
        except Exception as e:
            logger.error(f"Error while navigating to {url}: {e}")
            raise  # Re-raise the exception to stop further execution

    def response_err(self, request, url):
        if request.ok:
            pass
        else:
            print(f"Error while requesting {url}: {request.status_code}")
            raise Exception(f"Error while requesting {url}: {request.status_code}")
    def loc_err(self, soup, link, element):
        if soup == None:
            print(f"Error while locating {element} in {link}")
            raise Exception(f"Error while locating {element} in {link}")
        
    def embed_url(self, ep_url):
        try:
            
            r = self.session.get(ep_url)
            print("r", r)
            self.response_err(r, ep_url)
            
            soup = BeautifulSoup(r.content, "html.parser")
            print("soup", soup)
            link = soup.find("a", {"class": "active", "rel": "1"})
            print("link", link)
            self.loc_err(link, ep_url, "embed-url")
            ep_url = f'https:{link["data-video"]}' if not link["data-video"].startswith("https:") else link["data-video"]
            return ep_url
            
        except Exception as e:
            logger.error(f"Error while getting embed url: {e}")
            
    def get_data(self, ep_url):
        request = self.session.get(ep_url)
        print("request", request)
        soup = BeautifulSoup(request.content, "html.parser")
        print("soup", soup)
        crypto = soup.find("script", {"data-name": "episode"})

        self.loc_err(crypto, ep_url, "token")
        print("crypto", crypto["data-value"])
        return crypto["data-value"]
    
    def get_enc_key(self, ep_url):
        page = self.session.get(ep_url).text
        
        keys = re.findall(r"(?:container|videocontent)-(\d+)", page)
        
        if not keys:
            return {}
        
        key,iv,second_key = keys
        return {
            "key": key.encode(),
            "iv": iv.encode(),
            "second_key": second_key.encode()
        }
        
    def aes_encrypt(self, data, key, iv):
        return base64.b64encode(
            AES.new(key, self.mode, iv=iv).encrypt(self.pad(data).encode())
        )

    def aes_decrypt(self, data, key, iv):

        
        return (
            AES.new(key, self.mode, iv=iv)
            .decrypt(base64.b64decode(data))
            .strip(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10")
        )

    def play_video(self, url):
        # play the video with mpv
        print(f"Playing {url}")
        mpv = MPV()
        #mpv = MPV(start_mpv=False, ipc_socket="/tmp/mpv-socket")
        mpv.command("loadfile", url)
        time.sleep(5)
        duration = mpv.get_property("duration")
        print(f"Duration: {duration} seconds")
        time.sleep(duration)
        mpv.command("stop")
        self.web_interactions.cleanup()
        
    def stream_url(self, ep_url):
        encryption_keys = self.get_enc_key(ep_url)
        print("encryption_key", encryption_keys)
        
        parsed_url = urlparse(ep_url)
        print("parsed_url", parsed_url)
        
        self.ajax_url = parsed_url.scheme + "://" + parsed_url.netloc + self.ajax_url
        print("ajax_url", self.ajax_url)
        
        data = self.aes_decrypt(
            self.get_data(ep_url), encryption_keys["key"], encryption_keys["iv"]
        ).decode()
        
        data = dict(parse_qsl(data))
        
        id = urlparse(ep_url).query
        id = dict(parse_qsl(id))["id"]
        print("id", id)
  
        encrypted_id = self.aes_encrypt(id, encryption_keys["key"], encryption_keys["iv"]).decode()
        print("encrypted_id", encrypted_id)
        data.update(id=encrypted_id)
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "referer": ep_url,
        }
        print(f"types: {type(data)} {type(self.ajax_url)} {type(headers)}")
        request = self.session.post(
            self.ajax_url +  urlencode(data) + f"&alias={id}", headers=headers)
        print("request", request)
        self.response_err(request, request.url)
        print("response")
        json_response = json.loads(
            self.aes_decrypt(request.json().get("data"), encryption_keys["second_key"], encryption_keys["iv"]))
        print("json_response", json_response)
        source_data = [x for x in json_response["source"]]
        self.quality(source_data)
        print("source_data", source_data)
        # source_data [{'file': 'https://www008.vipanicdn.net/streamhls/5488f3268d41f9148a85959cc1c1fb32/ep.2.1677599793.m3u8', 'label': 'hls P', 'type': 'hls'}]
        # play the video
        self.play_video(source_data[0]["file"])

    
    def quality(self, json_data):
        """
        Get quality options from
        JSON repons and change
        stream url to the either
        the quality option that was picked,
        or the best one avalible.
        """
        #self.entry.quality = ""

        streams = []
        for i in json_data:
            if "m3u8" in i["file"] or i["type"] == "hls":
                type = "hls"
            else:
                type = "mp4"

            quality = i["label"].replace(" P", "").lower()

            streams.append({"file": i["file"], "type": type, "quality": quality})

        filtered_q_user = list(filter(lambda x: x["quality"] == self.qual, streams))
        print("filtered_q_user", filtered_q_user)
        if filtered_q_user:
            stream = list(filtered_q_user)[0]
        elif self.qual == "best" or self.qual == None:
            stream = streams[-1]
        elif self.qual == "worst":
            stream = streams[0]
        else:
            stream = streams[-1]

        self.quality = stream["quality"]
        stream_url = stream["file"]
        print("stream_url", stream_url)

        
    def extract_m3u8_streams(uri):
        if re.match(r"https?://", uri):
            resp = requests.get(uri)
            resp.raise_for_status()
            raw_content = resp.content.decode(resp.encoding or "utf-8")
            base_uri = urljoin(uri, ".")
        else:
            with open(uri) as fin:
                raw_content = fin.read()
                base_uri = Path(uri)

        content = m3u8.M3U8(raw_content, base_uri=base_uri)
        content.playlists.sort(key=lambda x: x.stream_info.bandwidth)
        streams = []
        for playlist in content.playlists:
            streams.append(
                {
                    "file": urljoin(content.base_uri, playlist.uri),
                    "type": "hls",
                    "quality": str(playlist.stream_info.resolution[1]),
                }
            )

        return streams
    
    
    def logs_of_webdriver(self, driver):
        browser_log = driver.get_log('performance') 
        events = [process_browser_log_entry(entry) for entry in browser_log]
        events = [event for event in events if 'Network.response' in event['method']]
        events_str = json.dumps(events)
        self.file_operations.write_to_file('Logs/logs.txt', events_str)


    def main(self):
        try:
            user_input = input("Enter the anime you want to watch: ")
            animes = find_anime(user_input)
            if animes:
                print("Search results: ")
                for i, anime in enumerate(animes):
                    print(f"{i+1}. {anime['title']}") 

                   
                selected_index = input("Enter the index of the anime you want to watch (or 0 to exit): ")
                if selected_index == '0':
                    print("Exiting...")
                    return
                    
                if selected_index.isdigit() and 0 <= int(selected_index) <= len(animes):
                    selected_anime = animes[int(selected_index)-1]
                    print(f"Selected anime: {selected_anime['title']}")
                    prompt = input(self.naviguate_fetch_episodes(selected_anime['link']))
                    prompt = int(prompt)
                    
                    
                else:
                    print("Invalid input. Please enter a valid index.")
            else:
                print("Anime not found")
        except Exception as e:
            self.web_interactions.cleanup()
            logger.error(f"Error while watching anime: {e}")
            
            print("Exiting...")

    