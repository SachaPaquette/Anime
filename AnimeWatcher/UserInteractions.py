from AnimeWatcher.EpisodesList import animeList, episodesList
# Import logger
from Config.logs_config import setup_logging
from Config.config import AnimeWatcherConfig
# Import the logger
logger = setup_logging(AnimeWatcherConfig.ANIME_WATCH_LOG_FILENAME,AnimeWatcherConfig.ANIME_WATCH_LOG_PATH)


class UserInteractions:
    def __init__(self):
        self.quit_symbol = '0'

    def select_anime(self, animes):
        """
        Displays the search results and prompts the user to select an anime.

        Args:
            animes (list): List of anime dictionaries.

        Returns:
            int: The selected index of the anime, or 0 to exit.
        """
        
        return animeList(animes)

    def get_user_input(self, max_episode, watched_list=None):
        """
        Prompts the user to enter the episode they want to start watching, between the given start and max episodes.

        Args:
            start_episode (int): The first episode available to watch.
            max_episode (int): The last episode available to watch.

        Returns:
            str: The user's input, which is either a valid episode number or '0' to exit.
        """
        try:
            while True:
                # Prompt the user to enter the episode they want to start watching
                user_input = episodesList(max_episode, watched_list)
                # If the user wants to exit
                if user_input == self.quit_symbol:
                    exit()
                # If the user entered a valid episode, return the episode number
                return user_input
        except Exception as e:
            # If an error occurs while getting the user's input, log the error and raise it
            logger.error(f"Error while getting user input: {e}")
            raise
        except KeyboardInterrupt:
            # If the user presses Ctrl+C, exit the program
            exit()
