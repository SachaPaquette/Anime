from python_mpv_jsonipc import MPV


class VideoPlayer:
    # Create a singleton instance of the VideoPlayer class
    _instance = None

    def __new__(cls):
        """
        Create a new instance of the VideoPlayer class if it doesn't already exist.

        Returns:
            VideoPlayer: The instance of the VideoPlayer class.
        """
        if cls._instance is None:  # Check if the instance of the VideoPlayer class exists
            # If the instance doesn't exist, create a new instance
            cls._instance = super(VideoPlayer, cls).__new__(
                cls)  # Call the __new__ method of the superclass
            cls._instance.observer_id = None  # Initialize the observer ID to None
            cls._instance.mpv = MPV()  # Create a new instance of the MPV class
            # Options to be passed to the MPV instance
            cls._instance.mpv.fullscreen = True

        return cls._instance  # Return the instance of the VideoPlayer class

    def initialize_player(self):
        """
        Initialize the video player.

        This method initializes the video player by binding the property observer and setting the fullscreen property to True.
        """
        try:
            self.mpv = MPV()  # Create a new instance of the MPV class
            # Bind the property observer
            self.observer_id = self.mpv.bind_property_observer("idle-active", self.should_skip_video)
            # Set the fullscreen property to True
            self.mpv.fullscreen = True
        except Exception as e:
            raise e

    def play_video(self, url):
        try:
            # Check if the player is closed
            if self.is_closed():
                # Create a new instance of the MPV class
                self.initialize_player()
            # Play the video
            self.mpv.play(url)  # Play the video
        except Exception as e:
            # Recreate the MPV instance and try again if the socket is closed
            if "socket is closed" in str(e):
                self.initialize_player()
                self.play_video(url)
            else:
                raise e  # Re-raise the exception if it's not a socket closed error


    def should_skip_video(self, name, value):
        """
        Determines whether the video should be skipped based on the player's state.

        Args:
            name (str): The name of the property being observed.
            value (bool): The current value of the property.

        Returns:
            None
        """
        try:
            # If the player is not idle, return
            if not value:
                return

            keep_player_open = True  # Keep the player open by default
            # Check if the media player is idle
            if not keep_player_open:
                self.quit_command()  # Send the 'quit' command to the mpv player

            # Unbind the property observer
            self.mpv.unbind_property_observer(self.observer_id)
            self.observer_id = None
        except Exception as e:
            raise e  # Re-raise the exception to stop further execution
        
    def quit_command(self):
        """
        Sends the 'quit' command to the mpv player.
        """
        try:
            self.mpv.command("quit")
        except Exception as e:
            raise e
        
    def terminate_player(self):
        """
        Terminate the video player.

        This method unbinds the property observer, if any, and sends the 'quit' command to the mpv player.
        """
        try:
            if self.observer_id:
                # Unbind the property observer
                self.mpv.unbind_property_observer(self.observer_id)
                # Reset the observer ID to None
                self.observer_id = None
            # Send the 'quit' command to the mpv player
            self.quit_command()
            # Reset the instance to None (to allow the creation of a new instance)
            self._instance = None
            # Reset the instance of the VideoPlayer class to None (to allow the creation of a new instance)
            self.mpv = None
        except Exception as e:
            raise e

    def is_closed(self):
        # Check if the mpv instance is None
        return self.mpv is None
