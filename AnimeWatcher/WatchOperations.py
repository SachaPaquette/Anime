from Config.config import Config
from Config.logs_config import setup_logging
from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions
from database import find_anime
from AnimeWatcher.VideoPlayer import VideoPlayer
from AnimeWatcher.UrlOperations import UrlInteractions
from AnimeWatcher.EpisodeOperations import EpisodeMenu
from AnimeWatcher.UserInteractions import UserInteractions

# Configure the logger
logger = setup_logging('anime_watch', Config.ANIME_WATCH_LOG_PATH)

class AnimeWatch:
    def __init__(self, web_interactions=None, anime_interactions=None):
        """
        Initializes a new instance of the WatchOperations class.

        Args:
            web_interactions (WebInteractions, optional): An instance of the WebInteractions class. Defaults to None.
            anime_interactions (AnimeInteractions, optional): An instance of the AnimeInteractions class. Defaults to None.
        """
        self.web_interactions = web_interactions if web_interactions else WebInteractions()
        self.anime_interactions = anime_interactions if anime_interactions else AnimeInteractions(
            self.web_interactions)
        self.url_interactions = UrlInteractions(Config.QUALITY)  # default quality is best
        self.video_player = None  # Create an instance of VideoPlayer
        self.user_interactions = UserInteractions()
            
    def naviguate_fetch_episodes(self, url, anime_name):
        """
        Navigates to the given URL and fetches the episodes for the specified anime.

        Args:
            url (str): The URL to navigate to.
            anime_name (str): The name of the anime.

        Returns:
            bool: True if the application needs to be restarted, False otherwise.
        """
        try:
            # Navigate to the URL
            self.web_interactions.naviguate(url)
            # Get the start and max episodes from the page
            start_episode, max_episode = self.anime_interactions.get_number_episodes()
            # Get the user's input for the episode they want to start watching
            prompt = self.user_interactions.get_user_input(start_episode, max_episode, self.web_interactions, logger)
            # If the user wants to exit, return False to exit the program
            if prompt is None:
                self.web_interactions.exiting_statement()
                return True  # Signal to restart the application
            
            return self.handle_episodes(anime_name, prompt, start_episode, max_episode)

        except ValueError as ve:
            logger.error(f"Error while converting prompt to integer: {ve}")
            return False  # Signal to exit the program
        except KeyboardInterrupt:
            self.web_interactions.exiting_statement()
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False  # Signal to exit the program

    def format_and_play_episode(self, anime_name, prompt):
        """
        Formats the anime name, creates the episode URL, and plays the episode.

        Args:
            anime_name (str): The name of the anime.
            prompt (str): The user's input for the episode they want to start watching.

        Returns:
            str: The formatted episode URL.
        """
        # Format the anime name, create the episode URL, and play the episode
        anime_name = self.anime_interactions.format_anime_name(anime_name)
        episode_url = self.anime_interactions.format_episode_link(prompt, anime_name) # Format the episode URL
        self.play_episode(episode_url) # Play the episode
        return episode_url

    def handle_user_choice(self, prompt, start_episode, max_episode):
        """
        Handles the user's choice in the episode menu.

        Args:
            prompt (str): The current episode prompt.
            start_episode (int): The first episode available to watch.
            max_episode (int): The last episode available to watch.

        Returns:
            str: The updated episode prompt.
        """
        episode_menu = EpisodeMenu(start_episode, max_episode)
        episode_menu.display_menu()

        while True:
            user_choice = input("Enter your choice: ").lower()

            if user_choice in ['n', 'p', 'q', 'c']:
                # Handle the user's choice
                updated_prompt = episode_menu.handle_choice(user_choice, int(prompt))
                self.url_interactions = UrlInteractions("best")
                if updated_prompt is False:
                    # User wants to change the anime
                    self.web_interactions.exiting_statement()
                    self.video_player.terminate_player()
                    return False

                elif updated_prompt is None:
                    # User wants to quit the program
                    self.web_interactions.exiting_statement()
                    self.video_player.terminate_player()
                    return None

                else:
                    # User chose 'n' or 'p', update the prompt and continue
                    return updated_prompt

            else:
                print("Invalid choice. Please enter 'n', 'p', 'c' or 'q'.")


        

    def handle_episodes(self, anime_name, prompt, start_episode, max_episode):
        """
        Handles the episodes of an anime.

        Args:
            anime_name (str): The name of the anime.
            prompt (str): The user's choice.
            start_episode (int): The starting episode number.
            max_episode (int): The maximum episode number.

        Returns:
            bool: True if the user wants to change the anime, False if the user wants to quit the program.
        """
        while True:
            # Format the anime name, create the episode URL, and play the episode
            self.format_and_play_episode(anime_name, prompt)
            # Handle the user's choice
            prompt = self.handle_user_choice(prompt, start_episode, max_episode)
            # if the user wants to change anime
            if prompt is False:
                # User wants to change the anime 
                return True
            if prompt is None:
                # User wants to quit the program
                return False



    def play_episode(self, episode_url):
        """
        Plays the episode at the given URL.

        Args:
            episode_url (str): The URL of the episode to play.

        Raises:
            Exception: If an error occurs while playing the episode.
        """
        try:
            # Get the source data
            source_data = self.url_interactions.stream_url(episode_url)
            # Check if the video player is already running and create an instance if it's not
            if self.video_player is None:
                # Create an instance of VideoPlayer
                self.video_player = VideoPlayer()
            try:
                # Play the video
                self.video_player.play_video(source_data)
                return False

            except Exception as e:
                logger.error(f"Error while playing episode: {e}")
                raise

        except Exception as e:
            logger.error(f"Error while playing episode: {e}")
            raise
        except KeyboardInterrupt:
            self.web_interactions.exiting_statement()
            return None


class Main:


    def main(self):
        """
        Main function for watching anime.

        This function prompts the user to enter the anime they want to watch,
        searches for the anime, and allows the user to select an anime to watch.
        It then navigates to the selected anime's episodes and starts watching.

        Returns:
            None
        """
        self.user_interactions = UserInteractions()
        # Initialize the restart variable to True to start the loop
        restart = True

        while restart:
            # Create an instance of AnimeWatch
            anime_watch = AnimeWatch(None, None)

            try:
                # Prompt the user to enter the anime they want to watch
                user_input = input("Enter the anime you want to watch: ")
                # Search for the anime in the database
                animes = find_anime(user_input)
                # Check if the anime was found
                while not animes:
                    logger.warning(f"Anime '{user_input}' not found.")
                    # Re-prompt the user to enter the anime they want to watch
                    user_input = input("Enter the anime you want to watch: ")
                    animes = find_anime(user_input)

                # If the anime was found, prompt the user to select an anime to watch (ex: 1. Naruto)
                selected_index = self.user_interactions.select_anime(animes)
                # If the user selected the exit option, exit the program
                if selected_index == 0:
                    break  # Exit the loop and cleanup

                # Get the selected anime
                selected_anime = animes[selected_index - 1]
                # Print the selected anime
                print(f"Selected anime: {selected_anime['title']}")
                # Navigate to the selected anime's episodes and start watching
                restart = anime_watch.naviguate_fetch_episodes(
                    selected_anime['link'], selected_anime['title'])

            except Exception as e:
                logger.error(f"Error while watching anime: {e}")
                anime_watch.web_interactions.exiting_statement()
                restart = False  # Prevent the loop from restarting

            except KeyboardInterrupt:
                anime_watch.web_interactions.exiting_statement()
                break  # Exit the loop and cleanup

            finally:
                anime_watch.web_interactions.cleanup()  # cleanup the web instance

