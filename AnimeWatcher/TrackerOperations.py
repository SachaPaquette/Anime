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
logger = setup_logging(EpisodeTrackerConfig.EPISODE_TRACKER_LOG_FILENAME,EpisodeTrackerConfig.EPISODE_TRACKER_LOG_PATH)

class EpisodeTracker():
    def __init__(self):
        self.episode_list = []
        self.read_json_file()
    
    def read_json_file(self):
        """
        Read data from the JSON file and populate self.episode_list.

        If the file doesn't exist or encounters JSON decoding errors, log the appropriate message and handle the situation.
        """
        try:
            with open(EpisodeTrackerConfig.ANIME_WATCHER_JSON_FILE, 'r') as file:
                self.episode_list = json.load(file)
        except FileNotFoundError:
            logger.error("JSON file not found.")
            # Create an empty JSON file if it doesn't exist
            self.create_empty_file()
        except json.JSONDecodeError:
            logger.error("Error decoding JSON file.")
            self.episode_list = []  # Initialize with an empty list
        except Exception as e:
            logger.error(f"Error reading JSON file: {e}")
            self.episode_list = []  # Initialize with an empty list
            raise e
    
    def create_empty_file(self):
        """
        Create an empty JSON file at the specified path.
        """
        try:
            # Open the file in write mode and dump an empty list
            with open(EpisodeTrackerConfig.ANIME_WATCHER_JSON_FILE, 'w') as file:
                json.dump([], file)
        except Exception as e:
            logger.error(f"Error while creating empty JSON file: {e}")
            raise

    def add_anime(self, anime_name, min_episode_number, max_episode_number):
        """
        Add a new anime to the episode list with episodes initialized as not watched.

        Args:
            anime_name (str): The name of the anime to add.
            min_episode_number (int): The first episode number.
            max_episode_number (int): The last episode number.
        """
        try:
            # Add the anime to the episode_list
            self.episode_list.append({
                'title': anime_name,
                'episodes': [{'episode': num, 'watched': False} for num in range(min_episode_number, max_episode_number + 1)]
            })

            self.save_json_file()  # Save changes to JSON file

        except Exception as e:
            logger.error(f"Error while adding anime '{anime_name}': {e}")
            raise

        
    def update_anime(self, anime_name, episode_number):
        """
        Update the watched status of a specific episode for the given anime.

        Args:
            anime_name (str): The name of the anime.
            episode_number (int): The episode number to update as watched.
        """
        try:
            # Iterate through anime in episode_list
            for anime in self.episode_list:
                if anime['title'] == anime_name:
                    # Iterate through episodes of the matching anime
                    for episode in anime['episodes']:
                        if episode['episode'] == episode_number:
                            episode['watched'] = True
                            self.save_json_file()  # Save changes to JSON file
                            return  # Exit method after updating episode

            # If anime or episode is not found, log a warning
            logger.warning(f"Anime '{anime_name}' or episode {episode_number} not found.")

        except Exception as e:
            logger.error(f"Error while updating anime '{anime_name}', episode {episode_number}: {e}")
            raise

        
                
    def save_json_file(self):
        # Save the JSON file
        try:
            with open(EpisodeTrackerConfig.ANIME_WATCHER_JSON_FILE, 'w') as file:
                json.dump(self.episode_list, file, indent=4)
        except Exception as e:
            logger.error(f"Error saving JSON file: {e}")
            raise e
        
    def check_for_new_episodes(self, anime_name, max_episode):
        """
        Check if new episodes are available for an anime in the list.
        If new episodes are found, add them to the anime's episode list and save the changes to the JSON file.

        Args:
            anime_name (str): The name of the anime to check for new episodes.
            max_episode (int): The maximum episode number to check against.

        """
        for anime in self.episode_list:
            if anime['title'] == anime_name:
                current_max_episode = max(ep['episode'] for ep in anime['episodes'])
                if current_max_episode < max_episode:
                    # Add new episodes to the list
                    new_episodes = [{'episode': num, 'watched': False} for num in range(current_max_episode + 1, max_episode + 1)]
                    anime['episodes'].extend(new_episodes)
                    self.save_json_file()
                         
    def get_watched_list(self, anime_name, start_episode, end_episode):
        """
        Get the list of episodes that are watched for a given anime within the specified range.

        Args:
            anime_name (str): The name of the anime.
            start_episode (int): The starting episode number.
            end_episode (int): The ending episode number.

        Returns:
            list: A list of episode numbers that need to be watched.
        """
        for anime in self.episode_list:
            if anime['title'] == anime_name:
                # Check for and add any new episodes up to end_episode
                self.check_for_new_episodes(anime_name, end_episode)
                
                return [episode['episode'] for episode in anime['episodes']
                                    if start_episode <= episode['episode'] <= end_episode and not episode['watched']]
            
        # If the anime is not in the list, add it and return an empty list
        self.add_anime(anime_name, start_episode, end_episode)
        return []
        