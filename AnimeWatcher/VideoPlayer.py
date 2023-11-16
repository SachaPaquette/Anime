from python_mpv_jsonipc import MPV
import time

class VideoPlayer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VideoPlayer, cls).__new__(cls)
            cls._instance.observer_id = None
            cls._instance.mpv = MPV() 
        return cls._instance

    def play_video(self, url):
        self.mpv.play(url)
        time.sleep(5)  # Wait for the player to initialize

        # Bind a property observer for the idle-active property
        self.observer_id = self.mpv.bind_property_observer("idle-active", self.should_skip_video)

    def should_skip_video(self, name, value):
        if not value:
            return
        print("Video ended or skipped")
        
        self.mpv.unbind_property_observer(self.observer_id)
        self.observer_id = None
        self.mpv.command("quit")
        
    def terminate_player(self):
        if self.observer_id:
            self.mpv.unbind_property_observer(self.observer_id)
            self.observer_id = None
        self.mpv.command("quit")
    def reset_observer_id(self):
        self.observer_id = None