from python_mpv_jsonipc import MPV

class VideoPlayer:
    # Singleton instance of the VideoPlayer class
    _instance = None

    class VideoPlayer:
        def __new__(cls):
            """
            Create a new instance of the VideoPlayer class if one doesn't exist.

            Returns:
                VideoPlayer: The instance of the VideoPlayer class.
            """
            if cls._instance is None:
                cls._instance = super(VideoPlayer, cls).__new__(cls)
                cls._instance.observer_id = None
                cls._instance.mpv = None
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

        except Exception as e:
            # Recreate the MPV instance and try again if the socket is closed
            if "socket is closed" in str(e):
                # Terminate the MPV instance
                self.mpv = None
                # Reinitialize the MPV instance
                self.initialize_player()
                # Retry playing the video
                self.play_video(url)

            else:
                raise e

    def terminate(self):
        """
        Terminate the MPV instance.
        """
        try:
            if self.is_open():  # Replace with the appropriate method to check if the MPV instance is open
                self.mpv.command("quit")  # Corrected method call
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
            if self.mpv is not None:
                if self.observer_id:
                    self.mpv.unbind_property_observer(self.observer_id)
                    self.observer_id = None

                self.terminate()  # Terminate the MPV instance
                self._instance = None
                self.mpv = None  # Set mpv to None explicitly
        except (OSError, BrokenPipeError) as socket_error:
            # Handle socket closure gracefully (you can log the error or take other actions)
            print(f"Socket closure error: {socket_error}")
            raise socket_error
        except Exception as e:
            raise e

    def is_open(self):
        return self.mpv is not None

    def check_if_socket_is_open(self):
        """
        Check if the socket is open.
        """
        try:
            self.mpv.command("ignore")  # Corrected method call
            return True
        except Exception as e:
            return False
