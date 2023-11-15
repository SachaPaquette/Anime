from Config.config import Config
from Config.logs_config import setup_logging
from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions
from database import find_anime
from AnimeWatcher.FileOperations import FileOperations
from AnimeWatcher.VideoPlayer import VideoPlayer
from AnimeWatcher.UrlOperations import UrlInteractions

# Configure the logger
logger = setup_logging('anime_watch', Config.ANIME_WATCH_LOG_PATH)


class AnimeWatch:
    def __init__(self, web_interactions=None, anime_interactions=None):
        self.web_interactions = web_interactions if web_interactions else WebInteractions()
        self.anime_interactions = anime_interactions if anime_interactions else AnimeInteractions(
            self.web_interactions)
        self.file_operations = FileOperations()
        self.url_interactions = UrlInteractions("best")


    def naviguate_fetch_episodes(self, url):
        try:
            self.web_interactions.naviguate(url)
            start_episode, max_episode = self.anime_interactions.get_number_episodes()
            prompt = self.get_user_input(start_episode, max_episode)

            if prompt == '0':
                print("Exiting...")
                return

            if prompt.isdigit() and start_episode <= int(prompt) <= max_episode:
                anime_name = self.anime_interactions.format_anime_name_url(url)
                episode_url = self.anime_interactions.format_episode_link(
                    prompt, anime_name)
                self.play_episode(episode_url)
            else:
                print("Invalid input. Please enter a valid episode.")
                self.naviguate_fetch_episodes(url)
        except Exception as e:
            logger.error(f"Error while navigating to {url}: {e}")
            raise

    def get_user_input(self, start_episode, max_episode):
        return input(f"Enter the episode you want to start watching between {start_episode}-{max_episode} (or 0 to exit): ")

    def play_episode(self, episode_url):
        try:
            episode_url = self.url_interactions.embed_url(episode_url)
            source_data = self.url_interactions.stream_url(episode_url)
            video_player = VideoPlayer()
            video_player.play_video(source_data)
            self.web_interactions.cleanup()

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
                    prompt = input(anime_watch.naviguate_fetch_episodes(
                        selected_anime['link']))

                    if prompt.isdigit():
                        prompt = int(prompt)

                    else:
                        print(
                            "Invalid input for episode. Please enter a valid number.")
                        # recall the main function
                        self.main()
                else:
                    print("Invalid input. Please enter a valid index.")

            else:
                print("Anime not found")
        except Exception as e:
            anime_watch.web_interactions.cleanup()
            logger.error(f"Error while watching anime: {e}")

            print("Exiting...")
