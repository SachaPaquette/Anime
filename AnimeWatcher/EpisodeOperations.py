from AnimeWatcher.UserInteractions import UserInteractions
class Colors:
    # Class to store the colors used in the CLI
    red = '\033[91m' 
    green = '\033[92m'
    yellow = '\033[93m'
    orange = '\033[33m'
    endc = '\033[0m'

class EpisodeMenu:

    def __init__(self, start_episode, max_episode):
        # Initialize the start and max episode numbers
        self.start_episode = start_episode
        self.max_episode = max_episode
        # Initialize the color class
        self.color = Colors()
        self.user_interactions = UserInteractions()
    def reset_cli(self):
        """
        Resets the command line interface by clearing the screen.
        """
        print("\033c", end="")  # Clear the screen
    def reset_cli(self):
        print("\033c", end="") # Clear the screen 

    def display_menu(self):
        """
        Display the menu options for the AnimeWatcher application.
        """
        # Clear the screen before displaying the menu options
        self.reset_cli()
        # Display the menu options
        print("\n===== Menu =====\n") 
        print(f"{self.color.green}[N] Next Episode{self.color.endc}\n")
        print(f"{self.color.yellow}[P] Previous Episode{self.color.endc}\n")  
        print(f"{self.color.orange}[C] Change Anime{self.color.endc}\n")
        print(f"{self.color.red}[Q] Quit{self.color.endc}\n")

    def handle_choice(self, user_choice, current_episode):
        """
        Handles the user's choice and returns the appropriate episode or action.

        Parameters:
        - user_choice (str): The user's choice ('n', 'p', 'q', or 'c').
        - current_episode: The current episode.

        Returns:
        - The next episode if user_choice is 'n'.
        - The previous episode if user_choice is 'p'.
        - None if user_choice is 'q'.
        - False if user_choice is 'c'.
        - The current episode if user_choice is invalid.
        """
        # Handle the user's choice 
        # If the user enters 'n', return the next episode
        if user_choice == 'n':
            return self.next_episode(current_episode)
        # If the user enters 'p', return the previous episode
        elif user_choice == 'p':
            return self.previous_episode(current_episode)
        # If the user enters 'q', return None to quit the program
        elif user_choice == 'q':
            return None
        # If the user enters 'c', return False to change the anime
        elif user_choice == 'c':
            return self.change_anime()
        else:
            # If the user enters an invalid choice, print an error message and return the current episode
            print("Invalid choice. Please enter 'n', 'p', 'c' or 'q'.")
            return current_episode

    def next_episode(self, current_episode):
        """
        Returns the next episode number based on the current episode.

        Args:
            current_episode (int): The current episode number.

        Returns:
            int: The next episode number if available, otherwise returns the current episode number.
        """
        if current_episode < self.max_episode:
            return current_episode + 1
        else:
            print("No more episodes available.")
            return current_episode

    def previous_episode(self, current_episode):
        """
        Returns the previous episode number based on the current episode number.

        Args:
            current_episode (int): The current episode number.

        Returns:
            int: The previous episode number if it exists, otherwise the current episode number.
        """
        # Check if the current episode is greater than the start episode
        if current_episode > self.start_episode:
            # If the current episode is greater than the start episode, return the previous episode
            return current_episode - 1
        else:
            # If the current episode is equal to the start episode, print an error message and return the current episode
            print("Already at the first episode.")
            return current_episode
    def change_anime(self):
        """
        Change the current anime being watched by returning False to the main loop.

        Returns:
            bool:  False if the user wants to change the anime.
        """
        return False
    
    def available_choices(self):
        """
        Returns a list of the available choices for the user.

        Returns:
            list: A list of the available choices for the user.
        """
        return ['n', 'p', 'c', 'q']