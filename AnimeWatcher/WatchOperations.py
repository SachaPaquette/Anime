from Config.config import Config
from Config.logs_config import setup_logging
from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions
from database import find_anime
from AnimeWatcher.VideoPlayer import VideoPlayer
from AnimeWatcher.UrlOperations import UrlInteractions
from AnimeWatcher.EpisodeOperations import EpisodeMenu
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
        self.url_interactions = UrlInteractions(
            "best")  # default quality is best
        self.video_player = None  # Create an instance of VideoPlayer

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
            prompt = self.get_user_input(start_episode, max_episode)
            # If the user wants to exit, return False to exit the program
            if prompt is None:
                print("Exiting...")
                return True  # Signal to restart the application
            # Create an instance of EpisodeMenu to display the episode menu and handle the user's choice
            episode_menu = EpisodeMenu(start_episode, max_episode)

            while True:
                # Format the anime name (e.g "Jujutsu Kaisen" -> "jujutsu-kaisen")
                anime_name = self.anime_interactions.format_anime_name(
                    anime_name)
                print(f"Selected anime: {anime_name}")
                episode_url = self.anime_interactions.format_episode_link(
                    prompt, anime_name)
                print(f"Selected episode: {prompt}")
                self.play_episode(episode_url)

                episode_menu.display_menu()
                user_choice = input("Enter your choice: ").lower()
                self.url_interactions = UrlInteractions("best")

                prompt = episode_menu.handle_choice(user_choice, int(prompt))

                # if the user wants to change anime
                if prompt is False:
                    print("Exiting...")
                    self.video_player.terminate_player()  # terminate the video player
                    self.web_interactions.cleanup()  # cleanup the web instance
                    return True  # Signal to restart the application

                if prompt is None:
                    print("Exiting...")
                    self.video_player.terminate_player()  # terminate the video player
                    self.web_interactions.cleanup()  # cleanup the web instance
                    return False  # Signal to exit the program

        except Exception as e:
            logger.error(f"Error while navigating to {url}: {e}")
            return False  # Signal to exit the program

    def get_user_input(self, start_episode, max_episode):
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
                user_input = input(
                    f"Enter the episode you want to start watching between {start_episode}-{max_episode} (or 0 to exit): ")
                # If the user wants to exit, return None to exit the program
                if user_input == '0':
                    print("Exiting...")
                    return None
                # If the user entered a valid episode, return the episode number
                if user_input.isdigit() and start_episode <= int(user_input) <= max_episode:
                    return user_input
                # If the user entered an invalid episode, prompt them to enter a valid episode
                else:
                    print("Invalid input. Please enter a valid episode or '0' to exit.")
        except Exception as e:
            # If an error occurs while getting the user's input, log the error and raise it
            logger.error(f"Error while getting user input: {e}")
            raise
        except KeyboardInterrupt:
            # If the user presses Ctrl+C, exit the program
            print("Exiting...")
            return None

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
            print("\nExiting...")
            return None


class Main:
    def get_valid_index(self, prompt, max_index):
        """
        Prompts the user for an index and validates it.

        Args:
            prompt (str): The prompt message to display to the user.
            max_index (int): The maximum valid index.

        Returns:
            int: The valid index entered by the user.

        Raises:
            ValueError: If the user enters an invalid number.
        """
        while True:
            try:
                # Prompt the user to enter an index
                selected_index = int(input(prompt))
                # If the user entered a valid index, return it
                if selected_index == 0 or 0 <= selected_index <= max_index:
                    return selected_index  # Return the selected index
                else:
                    print("Invalid index. Please enter a valid index.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def select_anime(self, animes):
        """
        Displays the search results and prompts the user to select an anime.

        Args:
            animes (list): List of anime dictionaries.

        Returns:
            int: The selected index of the anime, or 0 to exit.
        """
        print("Search results: ")
        for i, anime in enumerate(animes):
            # Print the anime's title
            print(f"{i + 1}. {anime['title']}")
        # Prompt the user to enter the index of the anime they want to watch
        return self.get_valid_index("Enter the index of the anime you want to watch (or 0 to exit): ", len(animes))

    def main(self):
        """
        Main function for watching anime.

        This function prompts the user to enter the anime they want to watch,
        searches for the anime, and allows the user to select an anime to watch.
        It then navigates to the selected anime's episodes and starts watching.

        Returns:
            None
        """
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
                if animes:
                    # If the anime was found, prompt the user to select an anime to watch (ex: 1. Naruto)
                    selected_index = self.select_anime(animes)
                    # If the user selected the exit option, exit the program
                    if selected_index == 0:
                        print("Exiting...")
                        # Cleanup the web instance
                        anime_watch.web_interactions.cleanup()
                        # Exit the program by setting restart to False and continuing the loop
                        restart = False
                        continue
                    # Get the selected anime
                    selected_anime = animes[selected_index - 1]
                    # Print the selected anime
                    print(f"Selected anime: {selected_anime['title']}")
                    # Navigate to the selected anime's episodes and start watching
                    restart = anime_watch.naviguate_fetch_episodes(
                        selected_anime['link'], selected_anime['title'])

                else:
                    print("Anime not found")
                    anime_watch.web_interactions.cleanup()  # cleanup the web instance
                    # re-prompts the user to enter the anime they want to watch
                    continue

            except Exception as e:
                anime_watch.web_interactions.cleanup()  # cleanup the web instance
                # log the error
                logger.error(f"Error while watching anime: {e}")
                print("Exiting...")
                restart = False  # Prevent the loop from restarting
            except KeyboardInterrupt:
                print("\nExiting...")
                exit()  # exit the program
