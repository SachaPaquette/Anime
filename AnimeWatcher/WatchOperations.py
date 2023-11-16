from Config.config import Config
from Config.logs_config import setup_logging
from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions
from database import find_anime
from AnimeWatcher.FileOperations import FileOperations
from AnimeWatcher.VideoPlayer import VideoPlayer
from AnimeWatcher.UrlOperations import UrlInteractions
from AnimeWatcher.EpisodeOperations import EpisodeMenu
# Configure the logger
logger = setup_logging('anime_watch', Config.ANIME_WATCH_LOG_PATH)


class AnimeWatch:
    def __init__(self, web_interactions=None, anime_interactions=None):
        self.web_interactions = web_interactions if web_interactions else WebInteractions()
        self.anime_interactions = anime_interactions if anime_interactions else AnimeInteractions(
            self.web_interactions)
        self.file_operations = FileOperations()
        self.url_interactions = UrlInteractions("best")
        self.video_player = VideoPlayer()

    def naviguate_fetch_episodes(self, url, anime_name):
        try:
            self.web_interactions.naviguate(url)
            start_episode, max_episode = self.anime_interactions.get_number_episodes()
            prompt = self.get_user_input(start_episode, max_episode)

            if prompt is None:
                print("Exiting...")
                return

            episode_menu = EpisodeMenu(start_episode, max_episode)
            
            while True:
                anime_name = self.anime_interactions.format_anime_name(anime_name)
                episode_url = self.anime_interactions.format_episode_link(prompt, anime_name)
                self.play_episode(episode_url)

                episode_menu.display_menu()
                user_choice = input("Enter your choice: ").lower()
                self.url_interactions = UrlInteractions("best")
                
                
                prompt = episode_menu.handle_choice(user_choice, int(prompt))
                
                if prompt is None:
                    print("Exiting...")
                    self.video_player.terminate_player()
                    self.web_interactions.cleanup()
                    # close the program
                    return
                
                    
        except Exception as e:
            logger.error(f"Error while navigating to {url}: {e}")
        except KeyboardInterrupt:
            print("Exiting...")
            self.web_interactions.cleanup()
            return




    def get_user_input(self, start_episode, max_episode):
            """
            Prompts the user to enter the episode they want to start watching, between the given start and max episodes.

            Args:
                start_episode (int): The first episode available to watch.
                max_episode (int): The last episode available to watch.

            Returns:
                str: The user's input, which is either a valid episode number or '0' to exit.
            """
            while True:
                user_input = input(f"Enter the episode you want to start watching between {start_episode}-{max_episode} (or 0 to exit): ")

                if user_input == '0':
                    print("Exiting...")
                    return None

                if user_input.isdigit() and start_episode <= int(user_input) <= max_episode:
                    return user_input
                else:
                    print("Invalid input. Please enter a valid episode or '0' to exit.")


        


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
                # Create the video player
                
                
                # Play the video
                self.video_player.play_video(source_data)
                # Cleanup the web instance
                #self.web_interactions.cleanup()
                return False

            except Exception as e:
                logger.error(f"Error while playing episode: {e}")
                raise




class Main:
    def main(self):
        anime_watch = AnimeWatch(None, None)

        try:
            user_input = input("Enter the anime you want to watch: ")
            animes = find_anime(user_input)
            if animes:
                print("Search results: ")
                for i, anime in enumerate(animes):
                    print(f"{i+1}. {anime['title']}")

                selected_index = input(
                    "Enter the index of the anime you want to watch (or 0 to exit): ")
                if selected_index == '0':
                    print("Exiting...")
                    return

                if selected_index.isdigit() and 0 <= int(selected_index) <= len(animes):
                    selected_anime = animes[int(selected_index) - 1]
                    print(f"Selected anime: {selected_anime['title']}")
                    input(anime_watch.naviguate_fetch_episodes(
                        selected_anime['link'], selected_anime['title']))
                    
                    
                        
                else:
                    print("Invalid input. Please enter a valid index.")

            else:
                print("Anime not found")
        except Exception as e:
            anime_watch.web_interactions.cleanup()
            logger.error(f"Error while watching anime: {e}")

            print("Exiting...")

