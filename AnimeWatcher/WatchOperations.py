from Config.config import AnimeWatcherConfig, WebOperationsConfig
from Config.logs_config import setup_logging
from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions
from AnimeWatcher.VideoPlayer import VideoPlayer
from AnimeWatcher.UrlOperations import UrlInteractions
from AnimeWatcher.EpisodeOperations import EpisodeMenu, Menu
from AnimeWatcher.UserInteractions import UserInteractions
from AnimeWatcher.TrackerOperations import EpisodeTracker
import os
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
        # Create an instance of WebInteractions
        self.web_interactions = web_interactions if web_interactions else WebInteractions(
        )  
        # Create an instance of AnimeInteractions
        self.anime_interactions = anime_interactions if anime_interactions else AnimeInteractions(
            self.web_interactions)  
        # Create an instance of UrlInteractions with the default quality (best)
        self.url_interactions = UrlInteractions(WebOperationsConfig.QUALITY)
        # Create an instance of VideoPlayer
        self.video_player = None  
        # Create an instance of UserInteractions
        self.user_interactions = UserInteractions()
        self.episode_menu = Menu()
        self.episode_tracker = EpisodeTracker()
        
        

    def navigate_fetch_episodes(self, url, anime_name):
        """
        navigates to the given URL and fetches the episodes for the specified anime.

        Args:
            url (str): The URL to navigate to.
            anime_name (str): The name of the anime.

        Returns:
            bool: True if the application needs to be restarted, False otherwise.
        """
        try:
            # navigate to the URL
            self.web_interactions.navigate(url)
            # Get the start and max episodes from the page
            start_episode, max_episode = self.anime_interactions.get_number_episodes()

            return self.handle_episodes(self.user_interactions.get_user_input(max_episode, self.episode_tracker.get_watched_list(anime_name, start_episode, max_episode)),
                                        start_episode, 
                                        max_episode, 
                                        url, 
                                        anime_name,
                                        )

        except KeyboardInterrupt:
            return False  # Signal to exit the program
        except Exception as e:
            logger.error(f"Unexpected error in navigate_fetch_episodes(): {e}")
            return False
    def close_session(self):
        try:
            # Close the video player
            self.video_player.terminate_player()
            # exit the program
            exit()
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
        episode_menu = EpisodeMenu(start_episode, max_episode)
        episode_menu.display_menu()
        self.url_interactions = UrlInteractions("best")

        while True:
            user_choice = input("Enter your choice: ").lower().strip()
            
            if user_choice in episode_menu.available_choices():
                choice_result = episode_menu.handle_choice(user_choice, int(prompt))
                
                if choice_result == self.episode_menu.ChangeAnime:
                    self.video_player.terminate_player()
                    return choice_result
                elif choice_result == self.episode_menu.Quit:
                    self.close_session()
                else:
                    return choice_result
            else:
                print(f"Invalid choice. Please enter one of the following: {', '.join(episode_menu.available_choices())}.")
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
            # Play the episode with the formatted URL
            self.play_episode(self.anime_interactions.format_episode_link(url, anime_name, prompt))
            # Return the formatted episode URL
            return self.anime_interactions.format_episode_link(url, anime_name, prompt)
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
        try:
            while True:
                if prompt == self.episode_menu.ChangeAnime:
                    return True
                elif prompt == self.episode_menu.Quit:
                    return False
                self.episode_tracker.update_anime(anime_name, int(prompt))
                self.format_and_play_episode(prompt, url, anime_name)
                prompt = self.handle_user_choice(prompt, start_episode, max_episode)
        except ValueError as ve:
            logger.error(f"Error while handling episodes: {ve}")
        except Exception as e:
            logger.error(f"Unexpected error while handling episodes: {e}")
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
            if self.video_player is None or self.video_player.is_open():
                # Create a new instance of VideoPlayer if one
                # doesn't exist or if the current instance is closed
                self.video_player = VideoPlayer()
                # Try to play the episode using the video player instance
                self.video_player.play_video(self.url_interactions.get_streaming_url(episode_url))
        except Exception as e:
            # If an error occurs while getting the streaming URL, log an error and raise an exception
            logger.error(f"Error while playing episode: {e}")
            raise
        except KeyboardInterrupt:
            # If the user interrupts the program execution, exit the program
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
            user_input = self.anime_watch.anime_interactions.format_anime_name_from_input(input("Enter the anime you want to watch: "))

            # Return the animes found
            return self.anime_watch.anime_interactions.find_anime_website(user_input), user_input
        except Exception as e:
            logger.error(f"Error while searching for anime: {e}")
            # If an error occurs, exit the program
            exit()


    def search_and_select_anime(self):
        """
        Searches for an anime based on user input and allows the user to select from the search results.

        Returns:
            The selected anime object or None if the user cancels the selection.
        """
        try:
            while True:
                animes, user_input = self.find_anime_from_input()

                if not animes:
                    print(f"{user_input} was not found.")
                    continue

                selected_index = self.user_interactions.select_anime(animes)
                if selected_index == 0:
                    return None

                return animes[selected_index - 1]

        except Exception as e:
            logger.error(f"Error while searching and selecting anime: {e}")
            exit()


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
            # navigate to the anime's page and fetch the episodes for the anime
            return self.anime_watch.navigate_fetch_episodes(selected_anime['link'], selected_anime['title'])
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
            while True:
                selected_anime = self.search_and_select_anime()
                if selected_anime is None:
                    break  # Exit the loop if no anime is selected
                restart = self.watch_selected_anime(selected_anime)
                if not restart:
                    break  # Exit the loop if the user does not want to restart
        except KeyboardInterrupt:
            print("\nProgram interrupted. Exiting...")
        except Exception as e:
            logger.error(f"Unexpected exception: {e}")
        finally:
            self.anime_watch.web_interactions.cleanup()
            print("Cleanup completed.")

