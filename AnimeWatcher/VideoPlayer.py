from python_mpv_jsonipc import MPV
import time

class VideoPlayer:
    # Create a singleton instance of the VideoPlayer class
    _instance = None

    def __new__(cls):
        """
        Create a new instance of the VideoPlayer class if it doesn't already exist.

        Returns:
            VideoPlayer: The instance of the VideoPlayer class.
        """
        if cls._instance is None: # Check if the instance of the VideoPlayer class exists
            # If the instance doesn't exist, create a new instance
            cls._instance = super(VideoPlayer, cls).__new__(cls) # Call the __new__ method of the superclass
            cls._instance.observer_id = None # Initialize the observer ID to None
            cls._instance.mpv = MPV()  # Create a new instance of the MPV class
        return cls._instance # Return the instance of the VideoPlayer class

    def play_video(self, url):
        self.mpv.play(url)
        #time.sleep(5)  # Wait for the player to initialize

        # Bind a property observer for the idle-active property
        self.observer_id = self.mpv.bind_property_observer("idle-active", self.should_skip_video)

    def should_skip_video(self, name, value):
        """
        Determines whether the video should be skipped based on the player's state.

        Args:
            name (str): The name of the property being observed.
            value (bool): The current value of the property.

        Returns:
            None
        """
        # If the player is not idle, return
        if not value:
            return
        
        keep_player_open = True  # Keep the player open by default 
        # Check if the media player is idle
        if not keep_player_open:
            self.mpv.command("quit")

        # Unbind the property observer
        self.mpv.unbind_property_observer(self.observer_id)
        self.observer_id = None
        
    def terminate_player(self):
        if self.observer_id:
            self.mpv.unbind_property_observer(self.observer_id)
            self.observer_id = None
        self.mpv.command("quit")
        
    def reset_observer_id(self):
        self.observer_id = None