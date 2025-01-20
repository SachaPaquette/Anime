from Config.logs_config import setup_logging
from Config.config import EpisodeTrackerConfig
import os
import json

# Setup logging
logger = setup_logging(EpisodeTrackerConfig.EPISODE_TRACKER_LOG_FILENAME,EpisodeTrackerConfig.EPISODE_TRACKER_LOG_PATH)

class EpisodeTracker():
    def __init__(self):
        self.episode_list = []
        self.episode_dict = {}
        self.read_json_file()

    def read_json_file(self):
        """
        Read data from the JSON file and populate self.episode_list.
        """
        try:
            if not os.path.exists(EpisodeTrackerConfig.ANIME_WATCHER_JSON_FILE):
                logger.warning("JSON file not found. Creating a new file.")
                self.create_empty_file()

            with open(EpisodeTrackerConfig.ANIME_WATCHER_JSON_FILE, 'r') as file:
                self.episode_list = json.load(file)

            # Convert watched episodes to sets for faster lookup
            for anime in self.episode_list:
                anime['watched_episodes'] = set(anime['watched_episodes'])
                self.episode_dict[anime['title']] = anime['watched_episodes']  # Store in dictionary

        except json.JSONDecodeError:
            logger.error("Error decoding JSON file. Reinitializing as an empty list.")
            self.episode_list = []
            self.create_empty_file()

        except Exception as e:
            logger.error(f"Error reading JSON file: {e}")
            self.episode_list = []
            raise e

    def create_empty_file(self):
        """ Create an empty JSON file. """
        try:
            directory = os.path.dirname(EpisodeTrackerConfig.ANIME_WATCHER_JSON_FILE)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            with open(EpisodeTrackerConfig.ANIME_WATCHER_JSON_FILE, 'w') as file:
                json.dump([], file)
            logger.info("Created a new empty JSON file.")

        except Exception as e:
            logger.error(f"Error creating empty JSON file: {e}")
            raise

    def add_anime(self, anime_name):
        """
        Add a new anime with no watched episodes initially.
        """
        try:
            self.episode_list.append({
                'title': anime_name,
                'watched_episodes': []  # Empty list for watched episodes
            })
            self.save_json_file()

        except Exception as e:
            logger.error(f"Error adding anime '{anime_name}': {e}")
            raise

    def update_anime(self, anime_name, episode_number):
        """
        Update the watched status for a specific episode.
        """
        try:
            for anime in self.episode_list:
                if anime['title'] == anime_name:
                    if episode_number not in anime['watched_episodes']:
                        anime['watched_episodes'].append(episode_number)
                        self.save_json_file()
                        return

            logger.warning(f"Anime '{anime_name}' or episode {episode_number} not found.")

        except Exception as e:
            logger.error(f"Error updating anime '{anime_name}', episode {episode_number}: {e}")
            raise

    def save_json_file(self):
        """ Save the updated JSON file. """
        try:
            with open(EpisodeTrackerConfig.ANIME_WATCHER_JSON_FILE, 'w') as file:
                json.dump(self.episode_list, file, indent=4)
        except Exception as e:
            logger.error(f"Error saving JSON file: {e}")
            raise e

    def get_watched_list(self, anime_name, start_episode, end_episode):
        """
        Get the list of unwatched episodes within the specified range.
        """
        # Directly access the anime's watched episodes from the dictionary for fast lookup
        watched_episodes = self.episode_dict.get(anime_name)

        if watched_episodes is None:
            # If anime is not found, add it and return an empty list
            self.add_anime(anime_name)
            return []

        # Create the set of all episodes in the given range
        total_episodes = set(range(start_episode, end_episode + 1))

        # Return the difference (unwatched episodes)
        unwatched_episodes = list(total_episodes - watched_episodes)
        return unwatched_episodes
