from python_mpv_jsonipc import MPV
from Config.logs_config import setup_logging
from Config.config import AnimeWatcherConfig

# Configure the logger
logger = setup_logging(AnimeWatcherConfig.ANIME_WATCH_LOG_FILENAME,
                       AnimeWatcherConfig.ANIME_WATCH_LOG_PATH)

class VideoPlayer:
    # Singleton instance of the VideoPlayer class
    _instance = None

    def __new__(cls):
        """
        Create a new instance of the VideoPlayer class if one doesn't exist.

        Returns:
            VideoPlayer: The instance of the VideoPlayer class.
        """
        # Check if an instance of the VideoPlayer class exists
        if cls._instance is None:
            # Create a new instance of the VideoPlayer class
            cls._instance = super(VideoPlayer, cls).__new__(cls)
            # Set the observer ID to None
            cls._instance.observer_id = None
            # Set the MPV instance to None
            cls._instance.mpv = None
            # Return the instance of the VideoPlayer class
            return cls._instance
        return cls._instance

    def initialize_player(self):
        """
        Initializes the video player by creating a new MPV instance and setting it to fullscreen mode.

        Raises:
            Exception: If there is an error initializing the player.
        """
        try:
            if self.mpv is not None:
                self.terminate_player()  # Terminate the existing player instance
            # Create a new MPV instance
            self.mpv = MPV()
            # Make the video player fullscreen by default
            self.mpv.fullscreen = True
        except Exception as e:
            raise e

    def play_video(self, url):
        """
        Play a video using the MPV player.

        Args:
            url (str): The URL of the video to be played.

        Raises:
            Exception: If an error occurs while playing the video.
        """
        try:
            # Initialize the MPV instance
            self.initialize_player()
            # Try to play the video
            self.mpv.play(url)
        except (OSError, BrokenPipeError):
            try:
                self.terminate_player()  # Ensure the player is properly terminated
                self.initialize_player()
                self.mpv.play(url)
            except Exception as e:
                logger.error(f"Error while playing video: {e}")
                raise e

    def terminate(self):
        """
        Terminate the MPV instance.
        """
        try:
            if self.is_open():  # Check if the MPV instance is open
                self.mpv.command("quit") # Send the quit command to the MPV instance
        except Exception as e:
            raise e

    def terminate_player(self):
        """
        Terminate the video player.

        This method terminates the MPV instance and cleans up any associated resources.

        Raises:
            OSError: If there is an error with the socket closure.
            Exception: If there is any other unexpected error.
        """
        try:
            if self.mpv:
                if self.observer_id:
                    self.mpv.unbind_property_observer(self.observer_id)
                    self.observer_id = None
                self.terminate()
                self._instance = None
                self.mpv = None
        except (OSError, BrokenPipeError) as socket_error:
            logger.error(f"Socket closure error: {socket_error}")
        except Exception as e:
            logger.error(f"Unexpected error during player termination: {e}")
            raise

    def is_open(self):
        """
        Check if the video player is open.

        Returns:
            bool: True if the video player is open, False otherwise.
        """
        return self.mpv is not None

    def check_if_socket_is_open(self):
        """
        Check if the socket is open.
        """
        try:
            # Ignore the command to check if the socket is open
            self.mpv.command("ignore")
            # If the socket is open, return True
            return True
        except Exception as e:
            # If the socket is closed, return False
            return False
