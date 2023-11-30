from Config.config import AnimeWatcherConfig, WebOperationsConfig
from Config.logs_config import setup_logging
from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions
from database import find_anime
from AnimeWatcher.VideoPlayer import VideoPlayer
from AnimeWatcher.UrlOperations import UrlInteractions
from AnimeWatcher.EpisodeOperations import EpisodeMenu
from AnimeWatcher.UserInteractions import UserInteractions

# Configure the logger
logger = setup_logging(AnimeWatcherConfig.ANIME_WATCH_LOG_FILENAME,
                       AnimeWatcherConfig.ANIME_WATCH_LOG_PATH)
class AnimeWatch:
    def __init__(self, web_interactions=None, anime_interactions=None):
        """
        Initializes a new instance of the WatchOperations class.

        Args:
            web_interactions (WebInteractions, optional): An instance of the WebInteractions class. Defaults to None.
            anime_interactions (AnimeInteractions, optional): An instance of the AnimeInteractions class. Defaults to None.
        """
        self.web_interactions = web_interactions if web_interactions else WebInteractions(
        )  # Create an instance of WebInteractions
        self.anime_interactions = anime_interactions if anime_interactions else AnimeInteractions(
            self.web_interactions)  # Create an instance of AnimeInteractions
        # Create an instance of UrlInteractions with the default quality (best)
        self.url_interactions = UrlInteractions(WebOperationsConfig.QUALITY)
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
            prompt = self.user_interactions.get_user_input(
                start_episode, max_episode, self.web_interactions, logger)
            # If the user wants to exit, return False to exit the program
            if prompt is None:
                # Exit the program
                self.web_interactions.exiting_statement()
                return True  # Signal to restart the application
            # Returns True if the user wants to change the anime and False if the user wants to quit the program
            return self.handle_episodes(prompt, start_episode, max_episode, url, anime_name)

        except ValueError as ve:
            logger.error(f"Error while converting prompt to integer: {ve}")
            return False  # Signal to exit the program
        except KeyboardInterrupt:
            self.web_interactions.exiting_statement()
            return False  # Signal to exit the program
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False  # Signal to exit the program

    def close_session(self):
        try:
            # Print the exiting statement
            self.web_interactions.exiting_statement()
            # Close the video player
            self.video_player.terminate_player()
            # self.url_interactions.close_session()
        except Exception as e:
            logger.error(f"Error while closing session: {e}")
            raise

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
        # Create an instance of EpisodeMenu and display the menu to the user
        episode_menu = EpisodeMenu(start_episode, max_episode)
        episode_menu.display_menu()

        while True:
            # Prompt the user to enter their choice (n: next episode, p: previous episode, c: change anime, q: quit)
            user_choice = input("Enter your choice: ").lower()
            # Check if the user's choice is valid (n, p, c, or q only are valid)
            if user_choice in episode_menu.available_choices():
                self.url_interactions = UrlInteractions("best")
                # Handle the user's choice
                updated_prompt = episode_menu.handle_choice(
                    user_choice, int(prompt))

                # User wants to change the anime
                if updated_prompt is False:
                    # Exit the program
                    self.video_player.terminate_player()
                    # self.close_session()
                    return False

                # User wants to quit the program
                elif updated_prompt is None:
                    # Exit the program
                    self.close_session()
                    return None
                # User chose 'n' or 'p', update the prompt and continue
                else:
                    # Update the prompt
                    return updated_prompt

            else:
                print(
                    f"Invalid choice. Please enter one of the following: {', '.join(episode_menu.available_choices())}.")

    def format_and_play_episode(self, prompt, url, anime_name):
        """
        Formats the episode link using the provided prompt, URL, and anime name,
        and then plays the episode.

        Args:
            prompt (str): The prompt to be used for formatting the episode link.
            url (str): The URL of the episode.
            anime_name (str): The name of the anime.

        Returns:
            str: The formatted episode URL.

        Raises:
            Exception: If there is an error formatting or playing the episode.
        """
        try:
            # Format the episode link using the prompt, URL, and anime name
            episode_url = self.anime_interactions.format_episode_link(
                url, anime_name, prompt)

            # Play the episode with the formatted URL
            self.play_episode(episode_url)
            # Return the formatted episode URL
            return episode_url
        except Exception as e:
            logger.error(f"Error formatting or playing episode: {e}")
            raise

    def handle_episodes(self, prompt, start_episode, max_episode, url, anime_name):
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
            try:
                # Format the episode link and play the episode
                self.format_and_play_episode(prompt, url, anime_name)
                # Get the user's choice for the episode to watch
                prompt = self.handle_user_choice(
                    prompt, start_episode, max_episode)
                # Check if the user wants to change the anime
                if prompt is False:
                    return True
                # Check if the user wants to quit the program
                if prompt is None:
                    return False
            except ValueError as ve:
                # If the user enters an invalid prompt, log an error and exit the program
                logger.error(f"Error while handling episodes: {ve}")
                self.web_interactions.exiting_statement()
                exit()
            except KeyboardInterrupt:
                # If the user interrupts the program execution, exit the program
                self.web_interactions.exiting_statement()
                exit()
            except Exception as e:
                # If an unexpected error occurs, log an error and exit the program
                logger.error(f"Unexpected error while handling episodes: {e}")
                self.web_interactions.exiting_statement()
                exit()

    def play_episode(self, episode_url):
        """
        Plays the episode at the given URL.

        Args:
            episode_url (str): The URL of the episode to play.

        Raises:
            Exception: If an error occurs while playing the episode.
        """
        try:
            # Get the streaming URL for the episode (m3u8 file format)
            source_data = self.url_interactions.get_streaming_url(episode_url)

            if self.video_player is None or self.video_player.is_open():
                # Create a new instance of VideoPlayer if one
                # doesn't exist or if the current instance is closed
                self.video_player = VideoPlayer()

            try:
                # Try to play the episode using the video player instance
                self.video_player.play_video(source_data)
            except Exception as e:
                # If an error occurs while playing the episode, log an error and raise an exception
                logger.error(f"Error while playing episode: {e}")
                raise
        except Exception as e:
            # If an error occurs while getting the streaming URL, log an error and raise an exception
            logger.error(f"Error while playing episode: {e}")
            raise
        except KeyboardInterrupt:
            # If the user interrupts the program execution, exit the program
            self.web_interactions.exiting_statement()
            return None


class Main:
    def __init__(self):
        """
        Initializes a new instance of the Main class.

        Parameters:
            None

        Returns:
            None
        """
        # Create an instance of UserInteractions
        self.user_interactions = UserInteractions()
        # Create an instance of AnimeWatch
        self.anime_watch = AnimeWatch(None, None)

    def find_anime_from_input(self):
        """
        Prompts the user to enter the anime they want to watch,
        finds the animes matching the user's input, and returns
        the found animes along with the user's input.

        Returns:
            tuple: A tuple containing the found animes and the user's input.
        """
        try:
            # Prompt the user to enter the anime they want to watch
            user_input = input("Enter the anime you want to watch: ")
            # Find the animes matching the user's input
            animes = find_anime(user_input)
            # Return the animes found
            return animes, user_input
        except Exception as e:
            logger.error(f"Error while searching for anime: {e}")
            # If an error occurs, exit the program
            exit()
        except KeyboardInterrupt:
            # If the user interrupts the program execution, exit the program
            self.anime_watch.web_interactions.exiting_statement()
            exit()

    def search_and_select_anime(self):
        """
        Searches for an anime based on user input and allows the user to select from the search results.

        Returns:
            The selected anime object or None if the user cancels the selection.
        """
        while True:
            # Prompt the user to enter the anime they want to watch
            animes, user_input = self.find_anime_from_input()
            # If animes were found, prompt the user to select an anime
            if animes:
                # Prompt the user to select an anime
                selected_index = self.user_interactions.select_anime(animes)
                # If the user wants to exit, return None
                if selected_index == 0:
                    return None
                # Return the selected anime
                return animes[selected_index - 1]
            else:
                # If no animes were found, log a warning
                print(f"{user_input} was not found.")

    def watch_selected_anime(self, selected_anime):
        """
        Watch the selected anime.

        Args:
            selected_anime (dict): A dictionary containing information about the selected anime.

        Returns:
            bool: True if the anime was watched successfully, False otherwise.
        """
        try:
            print(f"Selected anime: {selected_anime['title']}")
            # Navigate to the anime's page and fetch the episodes for the anime
            return self.anime_watch.naviguate_fetch_episodes(selected_anime['link'], selected_anime['title'])
        except Exception as e:
            logger.error(f"Error while watching anime: {e}")
            # Print the exiting statement
            self.anime_watch.web_interactions.exiting_statement()
            # Exit the program by returning False
            return False

    def main(self):
        """
        Main function that controls the anime watching operations.

        This function runs in a loop until the user wants to exit the program.
        It searches for an anime, selects it, and then watches the selected anime.
        If the user wants to exit, the loop breaks and the program cleans up.

        Raises:
            KeyboardInterrupt: If the user interrupts the program execution.

        """
        try:
            # Variable to control the loop
            restart = True
            # Loop until the user wants to exit the program
            while restart:
                # Search for the anime and select it
                selected_anime = self.search_and_select_anime()
                # If the user wants to exit, exit the loop
                if selected_anime is None:
                    break  # Exit the loop and cleanup
                # Watch the selected anime
                restart = self.watch_selected_anime(selected_anime)
            # Call the web instance cleanup function
            self.anime_watch.web_interactions.cleanup()
        except KeyboardInterrupt:
            # Print the exiting statement
            self.anime_watch.web_interactions.exiting_statement()
            # Call the web instance cleanup function
            self.anime_watch.web_interactions.cleanup()
            # Exit the program
            exit()
