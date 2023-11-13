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

logger = setup_logging('anime_watch', Config.ANIME_WATCH_LOG_PATH)
class Colors:
    GREEN = "\033[92m"
    END = "\x1b[0m"
class AnimeWatch:
    def __init__(self, web_interactions=None, anime_interactions=None):
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
                self.embed_url(self.anime_interactions.format_episode_link(prompt, anime_name))
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
        r = self.session.get(ep_url)
        self.response_err(r, ep_url)
        soup = BeautifulSoup(r.content, "html.parser")
        link = soup.find("a", {"class": "active", "rel": "1"})
        self.loc_err(link, ep_url, "embed-url")
        ep_url = f'https:{link["data-video"]}' if not link["data-video"].startswith("https:") else link["data-video"]
        print("entry", ep_url)

        
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

    