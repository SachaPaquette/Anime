from Config.logs_config import setup_logging
from Config.config import EpisodeTrackerConfig
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter, Retry
from Cryptodome.Cipher import AES
from urllib.parse import urlparse, parse_qsl, urlencode
import re
import base64
import json

# Setup logging
logger = setup_logging(EpisodeTrackerConfig.EPISODE_TRACKER_LOG_FILENAME,
                       EpisodeTrackerConfig.EPISODE_TRACKER_LOG_PATH)

class EpisodeTracker():
    def __init__(self):
        self.episode_list = []
        self.read_json_file()
    
    def read_json_file(self):
        # Read the JSON file
        try:
            with open(EpisodeTrackerConfig.ANIME_WATCHER_JSON_FILE, 'r') as file:
                self.episode_list = json.load(file)
        except FileNotFoundError:
            logger.error("JSON file not found.")
            # Create the JSON file if it doesn't exist
            self.create_empty_file()
        except json.JSONDecodeError:
            logger.error("Error decoding JSON file.")
            self.episode_list = []
        except Exception as e:
            logger.error(f"Error reading JSON file: {e}")
            self.episode_list = []
            raise e
    
    def create_empty_file(self):
        # Create an empty JSON file
        with open(EpisodeTrackerConfig.ANIME_WATCHER_JSON_FILE, 'w') as file:
            json.dump([], file)

    def add_anime(self, anime_name, min_episode_number, max_episode_number):
        # Add the anime to the list and populate the episode list with the episodes and if they have been watched
        self.episode_list.append({
        'title': anime_name,
        'episodes': [{'episode': num, 'watched': False} for num in range(min_episode_number, max_episode_number + 1)]})
        self.save_json_file()
        
    def update_anime(self, anime_name, episode_number):
        # Update the episode as watched
        for anime in self.episode_list:
            if anime['title'] == anime_name:
                for episode in anime['episodes']:
                    if episode['episode'] == episode_number:
                        episode['watched'] = True
                        self.save_json_file()
        
                
    def save_json_file(self):
        # Save the JSON file
        try:
            with open(EpisodeTrackerConfig.ANIME_WATCHER_JSON_FILE, 'w') as file:
                json.dump(self.episode_list, file, indent=4)
        except Exception as e:
            logger.error(f"Error saving JSON file: {e}")
            raise e
        
    def check_for_new_episodes(self, anime_name, max_episode):
        # Check if a new episode is available for an anime in the list
        for anime in self.episode_list:
            if anime['title'] == anime_name:
                current_max_episode = max(ep['episode'] for ep in anime['episodes'])
                if current_max_episode < max_episode:
                    # Add the new episodes to the list without switching the old episodes 
                    anime['episodes'].extend([{'episode': num, 'watched': False} for num in range(current_max_episode + 1, max_episode + 1)])
                    
                    self.save_json_file()
                         
    def get_watched_list(self, anime_name, start_episode, end_episode):
        # Get the list of episodes to watch
        for anime in self.episode_list:
            if anime['title'] == anime_name:
                self.check_for_new_episodes(anime_name, end_episode)
                return [episode['episode'] for episode in anime['episodes'] if start_episode <= episode['episode'] <= end_episode and not episode['watched']]
        
        # If the anime is not in the list, return an empty list and add the anime to the list
        self.add_anime(anime_name, start_episode, end_episode)
        return []
        