import re
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from database import  detect_duplicates
from tqdm import tqdm  # Import tqdm for the progress bar
import random
from Config.config import Config
from Config.logs_config import setup_logging
from Driver.driver_config import driver_setup
from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions
from database import find_anime
import subprocess
logger = setup_logging('anime_watch', Config.ANIME_WATCH_LOG_PATH)

class AnimeWatch:
    def __init__(self, web_interactions=None, anime_interactions=None):
        self.web_interactions = web_interactions if web_interactions else WebInteractions()
        self.anime_interactions = anime_interactions if anime_interactions else AnimeInteractions()
    
    def naviguate_to_anime(self, url):
        try:
            self.web_interactions.naviguate(url)
        except Exception as e:
            logger.error(f"Error while navigating to {url}: {e}")
            raise  # Re-raise the exception to stop further execution
    
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
                    self.naviguate_to_anime(selected_anime['url'])
                    
                else:
                    print("Invalid input. Please enter a valid index.")
            else:
                print("Anime not found")
        except Exception as e:
            logger.error(f"Error while watching anime: {e}")
            self.web_interactions.cleanup()
            print("Exiting...")

    