from python_mpv_jsonipc import MPV


class VideoPlayer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VideoPlayer, cls).__new__(cls)
            cls._instance.observer_id = None
            cls._instance.mpv = None  # Initialize mpv to None initially
            return cls._instance
        return cls._instance
    def initialize_player(self):
        try:
            if self.mpv is not None:
                self.terminate_player()  # Terminate the existing player instance

            self.mpv = MPV()
            self.mpv.fullscreen = True
        except Exception as e:
            raise e

    def play_video(self, url):
        try:
            self.initialize_player()
            self.mpv.play(url)
            
        except Exception as e:
            # Recreate the MPV instance and try again if the socket is closed
            if "socket is closed" in str(e):
                self.mpv = None
                self.initialize_player()
                self.play_video(url)
                
            else:
                raise e



    def quit_command(self):
        try:
            self.mpv.command("quit")
        except Exception as e:
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